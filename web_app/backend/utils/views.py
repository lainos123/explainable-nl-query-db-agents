from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import action
from django.conf import settings

from . import (
    extract_paths,
    extract_schema,
    schema_generation,
    schema_graph,
    sql_connector,
    get_keys,
)

MEDIA_ROOT = settings.MEDIA_ROOT

UTILITIES = {
    "extract-paths": "utils-extract-paths",
    "extract-schema": "utils-extract-schema",
    "schema-generation": "utils-schema-generation",
    "schema-graph": "utils-schema-graph",
    "sql-connect": "utils-sql-connect",
    "get-keys": "utils-get-keys",
}

class UtilsViewSet(viewsets.ViewSet):
    def list(self, request, format=None):
        # Return links to each utility action
        return Response({
            name: reverse(url_name, request=request, format=format)
            for name, url_name in UTILITIES.items()
        })

    @action(detail=False, methods=["post"])
    def extract_paths(self, request):
        result = extract_paths.run(request, media_path=MEDIA_ROOT)
        return Response(result)

    @action(detail=False, methods=["post"])
    def extract_schema(self, request):
        result = extract_schema.run(request, media_path=MEDIA_ROOT)
        return Response(result)

    @action(detail=False, methods=["post"])
    def schema_generation(self, request):
        result = schema_generation.run(request, media_path=MEDIA_ROOT)
        return Response(result)

    @action(detail=False, methods=["post"])
    def schema_graph(self, request):
        result = schema_graph.run(request, media_path=MEDIA_ROOT)
        return Response(result)

    @action(detail=False, methods=["post"])
    def sql_connect(self, request):
        result = sql_connector.run(request, media_path=MEDIA_ROOT)
        return Response(result)

    @action(detail=False, methods=["get"])
    def get_keys(self, request):
        result = get_keys.get_api_key()
        return Response({"api_key": result})
