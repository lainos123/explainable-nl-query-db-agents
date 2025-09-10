from django.shortcuts import render
from httpcore import Response
from .serializers import ChatHistorySerializer, FilesSerializer
from rest_framework import viewsets
from .models import ChatHistory, Files
from django.conf import settings

MEDIA_ROOT = settings.MEDIA_ROOT

# Create your views here.
class FilesViewSet(viewsets.ModelViewSet):
    # Allow mutliple file uploads with zip/.sql
    queryset = Files.objects.all()
    serializer_class = FilesSerializer

    # Handle file uploads
    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist('files')
        for file in files:
            # For zip
            if file.name.endswith('.zip'):
                # Unzip and save all files
                import zipfile
                with zipfile.ZipFile(file, 'r') as zip_ref:
                    zip_ref.extractall(MEDIA_ROOT)
        else:
            # For all other files
            Files.objects.create(file=file)
        return Response(status=201)



class ChatHistoryViewSet(viewsets.ModelViewSet):
    queryset = ChatHistory.objects.all()
    serializer_class = ChatHistorySerializer