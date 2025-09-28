from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(["GET"])
def api_root(request, format=None):
    return Response({
        "files-list": reverse("files-list", request=request, format=format),
        "apikeys": reverse("apikeys-list", request=request, format=format),
        "agents": reverse("agents-list", request=request, format=format),
        "schema": reverse("schema", request=request, format=format),
    })
