from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.conf import settings
from utils.get_keys import get_api_key
from . import a_db_select, b_table_select, c_sql_generate

MEDIA_ROOT = settings.MEDIA_ROOT

AGENTS = {
    "a-db-select": a_db_select.db_select,
    "b-table-select": b_table_select.table_select,
    "c-sql-generate": c_sql_generate.sql_generate,
}

class AgentViewSet(viewsets.ViewSet):
    def list(self, request, format=None):
        # List all available agents
        return Response({
            name: reverse("agents-detail", args=[name], request=request, format=format)
            for name in AGENTS.keys()
        })

    def retrieve(self, request, pk=None):
        # Run agent where pk = agent_name
        if pk not in AGENTS:
            return Response({"error": "Invalid agent"}, status=400)

        api_key = get_api_key()
        func = AGENTS[pk]
        result = func(api_key, request, media_path=MEDIA_ROOT)
        return Response(result, status=200)
