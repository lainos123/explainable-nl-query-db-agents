import json
import re
import os, zipfile
from django.core.files import File
from django.conf import settings
from django.utils.text import get_valid_filename
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from utils import schema_builder
from django.http import FileResponse

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

def save_to_model(django_file, safe_name):
    obj = Files()
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
                            if extracted_file.endswith("/"):
                                continue
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
                                saved.append(save_to_model(django_file, safe_name))

                # Case 2: SQLite file
                else:
                    if not is_valid_sqlite(name):
                        return Response(
                            {"error": f"Invalid file type `{name}`. Only SQLite files allowed."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    if re.search(r"[\\/]", name) or name.startswith(".") or not name.isascii():
                        return Response({"error": f"Invalid file name `{name}`."}, status=status.HTTP_400_BAD_REQUEST)

                    safe_name = sanitize_and_replace(name)
                    saved.append(save_to_model(file, safe_name))

            if not saved:
                return Response({"error": "No valid SQLite files found."}, status=status.HTTP_400_BAD_REQUEST)

            # After all files are saved, build schema files
            all_files = Files.objects.all()
            sql_file_paths = {
                f.database: f.file.path
                for f in all_files if f.file and os.path.isfile(f.file.path)
            }
            sql_file_paths_json = json.dumps(sql_file_paths, ensure_ascii=False)

            schema_builder.build_schema_ab(sql_file_paths_json) # Version similar with table.json - no FK PK (for Agent A/B)
            schema_builder.build_schema_c(sql_file_paths_json) # Version with FK PK (for Agent C)

            return Response(saved, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    # Clear all records, files, and schemas
    @action(detail=False, methods=["delete"])
    def clear(self, request, *args, **kwargs):
        try:
            # Delete DB files
            files = Files.objects.all()
            for f in files:
                if f.file and f.file.path and os.path.isfile(f.file.path):
                    os.remove(f.file.path)
            files.delete()

            # Wipe schema dir completely
            if os.path.exists(settings.SCHEMA_DIR):
                for root, dirs, files in os.walk(settings.SCHEMA_DIR):
                    for fname in files:
                        os.remove(os.path.join(root, fname))
                # if you want to delete subdirs too:
                for dname in dirs:
                    os.rmdir(os.path.join(root, dname))
            os.makedirs(settings.SCHEMA_DIR, exist_ok=True)

            # Re-create empty data dir
            os.makedirs(settings.DATA_DIR, exist_ok=True)

            return Response(
                {"status": "All files and schemas deleted."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        file_obj = self.get_object()
        if not file_obj.file or not os.path.exists(file_obj.file.path):
            return Response({"error": "File not found"}, status=404)
        return FileResponse(open(file_obj.file.path, "rb"), as_attachment=True, filename=os.path.basename(file_obj.file.name))

# Other viewsets #
class SessionsViewSet(OAuthRestrictedModelViewSet):
    queryset = Sessions.objects.all()
    serializer_class = SessionsSerializer


class ChatsViewSet(OAuthRestrictedModelViewSet):
    queryset = Chats.objects.all()
    serializer_class = ChatsSerializer

class APIKeyViewSet(OAuthRestrictedModelViewSet):
    serializer_class = APIKeySerializer

    def get_object(self):
        return APIKey.get_solo()

    def list(self, request):
        obj = self.get_object()
        return Response(APIKeySerializer(obj).data)

    def retrieve(self, request, pk=None):
        obj = self.get_object()
        return Response(APIKeySerializer(obj).data)

    def create(self, request):
        obj = self.get_object()
        serializer = APIKeySerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        obj = self.get_object()
        serializer = APIKeySerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        obj = self.get_object()
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
