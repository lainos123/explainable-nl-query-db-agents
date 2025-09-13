from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files import File
from django.conf import settings
import os, zipfile

from .models import Files, Sessions, Chats, APIKeys
from .serializers import (
    FilesSerializer,
    SessionsSerializer,
    ChatsSerializer,
    APIKeysSerializer,
)

class SafeModelViewSet(viewsets.ModelViewSet):
    """Base ViewSet with authentication + error handling for create"""

    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FilesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Files.objects.all()
    serializer_class = FilesSerializer

    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist("file")
        if not files:
            return Response(
                {"error": "No files uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        saved = []
        try:
            for file in files:
                if file.name.endswith(".zip"):
                    with zipfile.ZipFile(file, "r") as zip_ref:
                        for extracted_file in zip_ref.namelist():
                            file_path = zip_ref.extract(extracted_file, settings.MEDIA_ROOT)
                            if os.path.isfile(file_path):
                                with open(file_path, "rb") as f:
                                    django_file = File(f, name=os.path.basename(file_path))
                                    obj = Files(user=request.user)
                                    obj.save()
                                    obj.file.save(os.path.basename(file_path), django_file, save=True)
                                    saved.append(FilesSerializer(obj).data)
                else:
                    obj = Files.objects.create(user=request.user, file=file)
                    saved.append(FilesSerializer(obj).data)

            if not saved:
                return Response(
                    {"error": "No files were saved."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(saved, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SessionsViewSet(SafeModelViewSet):
    queryset = Sessions.objects.all()
    serializer_class = SessionsSerializer


class ChatsViewSet(SafeModelViewSet):
    queryset = Chats.objects.all()
    serializer_class = ChatsSerializer


class APIKeysViewSet(SafeModelViewSet):
    queryset = APIKeys.objects.all()
    serializer_class = APIKeysSerializer
