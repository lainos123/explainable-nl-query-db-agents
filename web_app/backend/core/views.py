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
from django.http import FileResponse
from utils import schema_builder

from .models import Files, Chats, APIKeys
from .serializers import (
    FilesSerializer,
    ChatsSerializer,
    APIKeysSerializer,
)

# Allow .sqlite, .sqlite0 .. .sqlite6
SQLITE_EXTENSIONS = [f".sqlite{i}" for i in range(7)] + [".sqlite"]


# Helpers #

def is_valid_sqlite(name: str) -> bool:
    return any(name.endswith(ext) for ext in SQLITE_EXTENSIONS)


def sanitize_and_replace(file_name: str, data_dir: str) -> str:
    safe_name = get_valid_filename(os.path.basename(file_name))
    full_path = os.path.join(data_dir, safe_name)
    if os.path.exists(full_path):
        os.remove(full_path)
    return safe_name


def save_to_model(django_file, safe_name, user):
    obj = Files(user=user)
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

    def get_queryset(self):
        return Files.objects.filter(user=self.request.user)

    def get_user_dirs(self, user):
        # MEDIA_ROOT/<user.id>/{data,schema}
        user_root = os.path.join(settings.MEDIA_ROOT, str(user.id))
        data_dir = os.path.join(user_root, "data")
        schema_dir = os.path.join(user_root, "schema")
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(schema_dir, exist_ok=True)
        return user_root, data_dir, schema_dir

    def create(self, request, *args, **kwargs):
        user = request.user
        _, data_dir, schema_dir = self.get_user_dirs(user)

        files = request.FILES.getlist("file")
        if not files:
            return Response({"error": "No files uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        saved = []
        try:
            for file in files:
                name = file.name

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

                            safe_name = sanitize_and_replace(base_name, data_dir)
                            with zip_ref.open(extracted_file) as f:
                                django_file = File(f, name=safe_name)
                                saved.append(save_to_model(django_file, safe_name, user))

                # Case 2: SQLite
                else:
                    if not is_valid_sqlite(name):
                        return Response(
                            {"error": f"Invalid file type `{name}`. Only SQLite files allowed."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    if re.search(r"[\\/]", name) or name.startswith(".") or not name.isascii():
                        return Response({"error": f"Invalid file name `{name}`."}, status=status.HTTP_400_BAD_REQUEST)

                    safe_name = sanitize_and_replace(name, data_dir)
                    saved.append(save_to_model(file, safe_name, user))

            if not saved:
                return Response({"error": "No valid SQLite files found."}, status=status.HTTP_400_BAD_REQUEST)

            # Build schema
            user_files = Files.objects.filter(user=user)
            sql_file_paths = {
                f.database: f.file.path
                for f in user_files if f.file and os.path.isfile(f.file.path)
            }
            sql_file_paths_json = json.dumps(sql_file_paths, ensure_ascii=False)

            schema_builder.build_schema_ab(sql_file_paths_json, schema_dir)
            schema_builder.build_schema_c(sql_file_paths_json, schema_dir)

            return Response(saved, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["delete"])
    def clear(self, request, *args, **kwargs):
        user = request.user
        _, data_dir, schema_dir = self.get_user_dirs(user)
        try:
            files = Files.objects.filter(user=user)
            for f in files:
                if f.file and f.file.path and os.path.isfile(f.file.path):
                    os.remove(f.file.path)
            files.delete()

            # Clear schema dir
            if os.path.exists(schema_dir):
                for root, dirs, files in os.walk(schema_dir):
                    for fname in files:
                        os.remove(os.path.join(root, fname))
                    for dname in dirs:
                        os.rmdir(os.path.join(root, dname))
            os.makedirs(schema_dir, exist_ok=True)
            os.makedirs(data_dir, exist_ok=True)

            return Response({"status": "All files and schemas deleted."}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        file_obj = self.get_object()
        if file_obj.user != request.user:
            return Response({"error": "Forbidden"}, status=403)
        if not file_obj.file or not os.path.exists(file_obj.file.path):
            return Response({"error": "File not found"}, status=404)
        return FileResponse(open(file_obj.file.path, "rb"),
                            as_attachment=True,
                            filename=os.path.basename(file_obj.file.name))


class ChatsViewSet(OAuthRestrictedModelViewSet):
    serializer_class = ChatsSerializer

    def get_queryset(self):
        return Chats.objects.filter(user=self.request.user)


class APIKeysViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, _ = APIKeys.objects.get_or_create(user=self.request.user)
        return obj

    def retrieve(self, request):
        obj = self.get_object()
        serializer = APIKeysSerializer(obj)
        return Response(serializer.data)

    def create(self, request):
        obj = self.get_object()
        new_value = request.data.get("key", "")
        obj.api_key = new_value
        obj.save(update_fields=["api_key"])
        return Response(
            {"message": "API key updated", "api_key": obj.api_key},
            status=status.HTTP_200_OK,
        )
