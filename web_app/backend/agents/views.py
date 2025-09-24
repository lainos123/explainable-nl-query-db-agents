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

                # Stop pipeline if error returned
                if isinstance(result, dict) and result.get("error"):
                    yield f"data: {json.dumps({'status': 'error', 'agent': name, 'time': now_str()}, ensure_ascii=False)}\n\n"
                    break

            # Pipeline finished
            yield f"data: {json.dumps({'status': 'finished', 'time': now_str()}, ensure_ascii=False)}\n\n"

            # Save last result to per-user cache
            cache.set(f"{CACHE_KEY_PREFIX}:{request.user.id}", result, None)

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
