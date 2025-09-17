import re
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

# Base ViewSet with authentication + error handling for create
class OAuthRestrictedModelViewSet(viewsets.ModelViewSet):
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

# ViewSets for each models

# File upload with zip extraction
class FilesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Files.objects.all()
    serializer_class = FilesSerializer

    # Handle multiple file uploads and zip extraction
    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist("file")
        if not files:
            return Response(
                {"error": "No files uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        saved = []
        # Utility list for sqlite extensions (to ver6, currently ver 3, 2025)
        sqlite_extensions = [f".sqlite{i}" for i in range(7)]
        try:
            for file in files:
                # If zip, extract and save each file inside
                if file.name.endswith(".zip"):
                    # Notice: Stream-based extraction and saving for RAM efficiency
                    with zipfile.ZipFile(file, "r") as zip_ref:
                        for extracted_file in zip_ref.namelist():
                            # Accept only .sqlite* files
                            # (! IMPORTANT SETTING)
                            if not any(extracted_file.endswith(ext) for ext in sqlite_extensions):
                                continue

                            # Prevent directory traversal attack (Cybersecurity measure)
                            target_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, extracted_file))
                            if not target_path.startswith(os.path.abspath(settings.MEDIA_ROOT)):
                                return Response({"error": "Illegal path in zip."}, status=status.HTTP_400_BAD_REQUEST)

                            # Prevent corrupted names in zip files (Cybersecurity measure)
                            if extracted_file.startswith("/") or extracted_file.startswith("\\"):
                                # If not ASCII
                                if not all(ord(c) < 128 for c in extracted_file):
                                    return Response(
                                        {"error": "Corrupted file name detected in zip file. Avoid / or \\ at the start of filenames."},
                                        status=status.HTTP_400_BAD_REQUEST,
                                    )

                            file_path = zip_ref.extract(extracted_file, settings.MEDIA_ROOT)
                            if os.path.isfile(file_path):
                                with open(file_path, "rb") as f:
                                    # Save to Django model
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

# ViewSets for Sessions, Chats, APIKeys
class SessionsViewSet(OAuthRestrictedModelViewSet):
    queryset = Sessions.objects.all()
    serializer_class = SessionsSerializer


class ChatsViewSet(OAuthRestrictedModelViewSet):
    queryset = Chats.objects.all()
    serializer_class = ChatsSerializer


class APIKeysViewSet(OAuthRestrictedModelViewSet):
    queryset = APIKeys.objects.all()
    serializer_class = APIKeysSerializer
