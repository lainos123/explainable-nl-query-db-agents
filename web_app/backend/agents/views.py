from django.http import StreamingHttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json
from django.core.cache import cache
from datetime import datetime

from core.models import APIKey
from utils import sql_connector
from . import a_db_select, b_table_select, c_sql_generate

AGENTS = [
    ("a-db-select", a_db_select.run),
    ("b-table-select", b_table_select.run),
    ("c-sql-generate", c_sql_generate.run),
    ("d-sql-connector", sql_connector.run_sql),
]

CACHE_KEY = "last_agent_result"


def get_api_key():
    obj = APIKey.get_solo()
    return obj.api_key if obj else None


class AgentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, pk=None):
        api_key = get_api_key()

        def now_str():
            return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        def event_stream():
            result = request.data  # initial input

            for name, func in AGENTS:
                # log start
                yield f"data: {json.dumps({'status': 'running', 'agent': name, 'time': now_str()}, ensure_ascii=False)}\n\n"
                try:
                    start_time = now_str()
                    result = func(api_key, result)
                    end_time = now_str()
                    yield f"data: {json.dumps({'agent': name, 'output': result, 'started_at': start_time, 'finished_at': end_time}, ensure_ascii=False)}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'agent': name, 'error': str(e), 'time': now_str()}, ensure_ascii=False)}\n\n"

            # pipeline end
            yield f"data: {json.dumps({'status': 'finished', 'time': now_str()}, ensure_ascii=False)}\n\n"

            cache.set(CACHE_KEY, result, None)

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        return response

    def list(self, request):
        data = cache.get(CACHE_KEY)
        if not data:
            return Response({"status": "no previous result"}, status=status.HTTP_404_NOT_FOUND)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["delete"], url_path="cache")
    def clear_cache(self, request):
        """Clear last cached agent result."""
        cache.delete(CACHE_KEY)
        return Response(status=status.HTTP_204_NO_CONTENT)
