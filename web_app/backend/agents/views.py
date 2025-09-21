# backend/agents/views.py
import json
from django.http import StreamingHttpResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from utils.get_keys import get_api_key
from utils import sql_connector
from . import a_db_select, b_table_select, c_sql_generate

AGENTS = [
    ("a-db-select", a_db_select.run),
    ("b-table-select", b_table_select.run),
    ("c-sql-generate", c_sql_generate.run),
    ("d-sql-connector", sql_connector.run),
]


class AgentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, pk=None):
        api_key = get_api_key()

        def event_stream():
            result = request.data  # initial input
            for name, func in AGENTS:
                try:
                    result = func(api_key, result)
                    yield f"data: {json.dumps({name: result}, ensure_ascii=False)}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({name: {'error': str(e)}}, ensure_ascii=False)}\n\n"

        return StreamingHttpResponse(event_stream(), content_type="text/event-stream")
