from django.http import StreamingHttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json
from django.core.cache import cache
from datetime import datetime

from core.models import APIKeys
from utils import sql_connector
from django.http import StreamingHttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json
from django.core.cache import cache
from datetime import datetime

from core.models import APIKeys
from utils import sql_connector
from . import a_db_select, b_table_select, c_sql_generate
from utils.schema_builder import get_schema_dir
import os
import threading
import time
from django.utils import timezone
from core.models import DailyUsage
from core.limit_rate import has_chat_quota, increment_user_chats

# Pipeline agents
AGENTS = [
    ("a-db-select", a_db_select.run),
    ("b-table-select", b_table_select.run),
    ("c-sql-generate", c_sql_generate.run),
    ("d-sql-connector", sql_connector.run_sql),
]

# Cache key prefix (per user)
CACHE_KEY_PREFIX = "last_agent_result"


def get_api_key(user):
    """Return the API key for the given user, or None if not set."""
    try:
        return APIKeys.objects.get(user=user).api_key
    except APIKeys.DoesNotExist:
        return None


class AgentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, pk=None):
        """Run the full agent pipeline as an SSE stream."""
        api_key = get_api_key(request.user)

        # Quick pre-check: block request if user has no chat quota left for today.
        try:
            if not has_chat_quota(request.user):
                return Response({"error": "Daily chat limit reached."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except Exception:
            # If quota check fails for any reason, allow the request to proceed rather than blocking
            # (fail-open to avoid denying service on incidental errors).
            pass

        def now_str():
            return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        def event_stream():
            result = request.data  # initial input (dict from client)

            # Ensure API key exists before running any agent that calls LLMs
            if not api_key:
                payload = {
                    "status": "error",
                    "agent": "bootstrap",
                    "error": "Missing API key. Please set your API key in profile settings.",
                    "time": now_str(),
                }
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'status': 'finished', 'time': now_str()}, ensure_ascii=False)}\n\n"
                cache.set(f"{CACHE_KEY_PREFIX}:{request.user.id}", {"error": "Missing API key"}, None)
                return

            for name, func in AGENTS:
                # Announce agent start
                yield f"data: {json.dumps({'status': 'running', 'agent': name, 'time': now_str()}, ensure_ascii=False)}\n\n"

                # Run agent in background thread so we can emit heartbeats while it works
                start_time = now_str()
                result_container = {}

                def target():
                    try:
                        result_container['result'] = func(api_key, result, request.user.id)
                    except Exception as e:
                        result_container['result'] = {'error': str(e)}

                t = threading.Thread(target=target, daemon=True)
                t.start()

                # While the agent thread is running, emit lightweight comments as keepalive
                # (colon-prefixed lines are SSE comments and act as heartbeats)
                while t.is_alive():
                    try:
                        yield ":\n\n"
                        time.sleep(0.8)
                    except GeneratorExit:
                        # client disconnected
                        return

                # Agent finished
                end_time = now_str()
                result = result_container.get('result')

                payload = {
                    "agent": name,
                    "output": result,
                    "started_at": start_time,
                    "finished_at": end_time,
                }
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

                # Increment user's chat usage for each meaningful response emitted by an agent.
                try:
                    # Only increment when the agent produced a non-error output
                    if not (isinstance(result, dict) and result.get('error')):
                        new_count = increment_user_chats(request.user, amount=1)
                        try:
                            # read user's limit
                            max_chats = getattr(request.user.userlimits, 'max_chats', 0)
                        except Exception:
                            max_chats = 0

                        # If user reached or exceeded their limit as a result of this increment,
                        # emit an error event and stop the pipeline to prevent further work.
                        if new_count is not None and max_chats and new_count >= max_chats:
                            yield f"data: {json.dumps({'status': 'error', 'agent': name, 'error': 'Daily chat limit reached during run', 'time': now_str()}, ensure_ascii=False)}\n\n"
                            break
                except Exception:
                    # Do not break the stream if increment or limit-check fails
                    pass

                # Stop pipeline if error returned
                if isinstance(result, dict) and result.get("error"):
                    yield f"data: {json.dumps({'status': 'error', 'agent': name, 'time': now_str()}, ensure_ascii=False)}\n\n"
                    break

            # Pipeline finished
            # Build final usage payload (do not mutate usage here; increments occurred during the stream)
            final_usage_payload = None
            try:
                today = timezone.now().date()
                du, _ = DailyUsage.objects.get_or_create(user=request.user, date=today, defaults={'chats_used': 0})

                # compute used_bytes and limits for final payload
                from core.models import Files, UserLimits
                from django.db.models import Sum
                agg = Files.objects.filter(user=request.user).aggregate(total=Sum('size'))
                used_bytes = int(agg.get('total') or 0)
                limits, _ = UserLimits.objects.get_or_create(user=request.user)
                GB = 1024 ** 3
                now = timezone.now()
                next_day = (now + timezone.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                seconds_until_reset = int((next_day - now).total_seconds())
                final_usage_payload = {
                    'max_chats': limits.max_chats,
                    'max_gb': limits.max_gb_db,
                    'chats_used_today': du.chats_used,
                    'used_bytes': used_bytes,
                    'max_bytes': int(limits.max_gb_db) * GB,
                    'seconds_until_reset': seconds_until_reset,
                    'server_time': now.isoformat(),
                    'reset_time': next_day.isoformat(),
                }
            except Exception:
                # avoid crashing the stream on usage tracking errors
                final_usage_payload = None

            # Emit final usage payload (if available) so clients can update UI immediately
            try:
                if final_usage_payload:
                    yield f"data: {json.dumps({'usage': final_usage_payload}, ensure_ascii=False)}\n\n"
            except Exception:
                pass

            yield f"data: {json.dumps({'status': 'finished', 'time': now_str()}, ensure_ascii=False)}\n\n"

            # Save last result to per-user cache including usage so GET /api/agents/ returns both
            try:
                cache_value = {'result': result, 'usage': final_usage_payload}
                cache.set(f"{CACHE_KEY_PREFIX}:{request.user.id}", cache_value, None)
            except Exception:
                try:
                    cache.set(f"{CACHE_KEY_PREFIX}:{request.user.id}", result, None)
                except Exception:
                    pass

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"  # disable proxy buffering (important for SSE)
        return response

    def list(self, request):
        """Return the last cached pipeline result for this user."""
        data = cache.get(f"{CACHE_KEY_PREFIX}:{request.user.id}")
        if not data:
            return Response({"status": "no previous result"}, status=status.HTTP_404_NOT_FOUND)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["delete"], url_path="cache")
    def clear_cache(self, request):
        """Clear last cached agent result for this user."""
        cache.delete(f"{CACHE_KEY_PREFIX}:{request.user.id}")
        return Response(status=status.HTTP_204_NO_CONTENT)
