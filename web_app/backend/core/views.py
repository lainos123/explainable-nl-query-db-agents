import re
import os, zipfile
from django.core.files import File
from django.conf import settings
from django.utils.text import get_valid_filename
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action


from .models import Files, Sessions, Chats, APIKey
from .serializers import (
    FilesSerializer,
    SessionsSerializer,
    ChatsSerializer,
    APIKeySerializer,
)

# Allow .sqlite, .sqlite0 .. .sqlite6
SQLITE_EXTENSIONS = [f".sqlite{i}" for i in range(7)] + [".sqlite"]


## Helpers ##

def is_valid_sqlite(name: str) -> bool:
    return any(name.endswith(ext) for ext in SQLITE_EXTENSIONS)


def sanitize_and_replace(file_name: str) -> str:
    # Remove path, ensure safe name, replace if exists
    safe_name = get_valid_filename(os.path.basename(file_name))
    full_path = os.path.join(settings.DATA_DIR, safe_name)
    if os.path.exists(full_path):
        os.remove(full_path)  # replace old file
    return safe_name

def save_to_model(user, django_file, safe_name):
    obj = Files(user=user)
    # Set database name without extension
    obj.database = os.path.splitext(safe_name)[0]
    obj.save()
    obj.file.save(safe_name, django_file, save=True)
    return FilesSerializer(obj).data

# Base OAuth ViewSet #
class OAuthRestrictedModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# File upload #
class FilesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Files.objects.all()
    serializer_class = FilesSerializer

    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist("file")
        if not files:
            return Response({"error": "No files uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        saved = []

        try:
            for file in files:
                name = file.name

                # Reject RAR
                if name.endswith(".rar"):
                    return Response(
                        {"error": "RAR files are not supported. Please upload ZIP or SQLite files."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Case 1: ZIP
                if name.endswith(".zip"):
                    with zipfile.ZipFile(file, "r") as zip_ref:
                        for extracted_file in zip_ref.namelist():
                            # Skip directories
                            if extracted_file.endswith("/"):
                                continue
                            # Reject non-SQLite files
                            if not is_valid_sqlite(extracted_file):
                                continue

                            base_name = os.path.basename(extracted_file)
                            if not base_name or not base_name.isascii():
                                return Response(
                                    {"error": f"Invalid file name in zip: {extracted_file}"},
                                    status=status.HTTP_400_BAD_REQUEST,
                                )

                            safe_name = sanitize_and_replace(base_name)
                            with zip_ref.open(extracted_file) as f:
                                django_file = File(f, name=safe_name)
                                saved.append(save_to_model(request.user, django_file, safe_name))

                # Case 2: SQLite file
                else:
                    if not is_valid_sqlite(name):
                        return Response(
                            {"error": f"Invalid file type `{name}`. Only SQLite files allowed."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Check file name safe
                    if re.search(r"[\\/]", name) or name.startswith(".") or not name.isascii():
                        return Response({"error": f"Invalid file name `{name}`."}, status=status.HTTP_400_BAD_REQUEST)

                    safe_name = sanitize_and_replace(name)
                    saved.append(save_to_model(request.user, file, safe_name))

            if not saved:
                return Response({"error": "No valid SQLite files found."}, status=status.HTTP_400_BAD_REQUEST)

            return Response(saved, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Clear all records and files
    @action(detail=False, methods=["delete"])
    def clear(self, request, *args, **kwargs):
        try:
            files = Files.objects.all()
            for f in files:
                if f.file and f.file.path and os.path.isfile(f.file.path):
                    os.remove(f.file.path)
            files.delete()
            # Re-create empty data directory
            os.makedirs(settings.DATA_DIR, exist_ok=True)
            return Response(
                {"status": "All files and their data deleted."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Other viewsets #
class SessionsViewSet(OAuthRestrictedModelViewSet):
    queryset = Sessions.objects.all()
    serializer_class = SessionsSerializer


class ChatsViewSet(OAuthRestrictedModelViewSet):
    queryset = Chats.objects.all()
    serializer_class = ChatsSerializer


class APIKeyViewSet(viewsets.ModelViewSet):
    serializer_class = APIKeySerializer
    queryset = APIKey.objects.none()

    def get_object(self):
        return APIKey.get_solo()
