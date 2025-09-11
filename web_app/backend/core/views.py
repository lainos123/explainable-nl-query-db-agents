from django.shortcuts import render
from httpcore import Response
from .serializers import FilesSerializer, SessionsSerializer, ChatsSerializer, APIKeysSerializer
from rest_framework import viewsets
from .models import Files, Sessions, Chats, APIKeys
from django.conf import settings
from rest_framework.permissions import IsAuthenticated

MEDIA_ROOT = settings.MEDIA_ROOT

# Create your views here.
class FilesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    # Allow mutliple file uploads with zip/.sql
    queryset = Files.objects.all()
    serializer_class = FilesSerializer

    # Handle file uploads
    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist('files')
        saved = []
        for file in files:
            # For zip
            if file.name.endswith('.zip'):
                # Unzip and save all files
                import zipfile
                with zipfile.ZipFile(file, 'r') as zip_ref:
                    zip_ref.extractall(MEDIA_ROOT)
        else:
            # For all other files
            obj = Files.objects.create(file=file, user=request.user)
            saved.append(FilesSerializer(obj).data)
        return Response(saved, status=201)

class SessionsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Sessions.objects.all()
    serializer_class = SessionsSerializer

class ChatsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Chats.objects.all()
    serializer_class = ChatsSerializer

class APIKeysViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = APIKeys.objects.all()
    serializer_class = APIKeysSerializer