import json
from django.http import StreamingHttpResponse
from rest_framework import viewsets
from utils.get_keys import get_api_key
from django.conf import settings
from . import a_db_select, b_table_select, c_sql_generate

MEDIA_ROOT = settings.MEDIA_ROOT

AGENTS = {
    "a-db-select": a_db_select.run,
    "b-table-select": b_table_select.run,
    "c-sql-generate": c_sql_generate.run,
}

class AgentViewSet(viewsets.ViewSet):
    def create(self, request, pk=None):
        api_key = get_api_key()
        # SSE response generator
        def event_stream():
            # Initial input to the first agent
            result = request.data
            for name, func in AGENTS.items():
                try:
                    result = func(api_key, result, media_path=MEDIA_ROOT)
                    # Stream each agent as a separate JSON object with \n\n
                    yield f"data: {json.dumps({name: result})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({name: 'error', 'detail': str(e)})}\n\n"

        return StreamingHttpResponse(event_stream(), content_type="text/event-stream")
