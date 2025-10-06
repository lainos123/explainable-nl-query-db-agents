import json
import re
import os
import zipfile
from django.core.files import File
from django.utils.text import get_valid_filename
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.http import FileResponse

from utils import schema_builder

from django.utils import timezone
from datetime import date

from .models import Files, DailyUsage, UserLimits
from django.db import IntegrityError
from .serializers import FilesSerializer
from .limit_rate import GBLimitMixin
from django.db.models import Sum

SQLITE_EXTENSIONS = [f".sqlite{i}" for i in range(7)] + [".sqlite"]


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


class OAuthRestrictedModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FilesViewSet(GBLimitMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Files.objects.all()
    serializer_class = FilesSerializer

    def get_queryset(self):
        return Files.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        files = request.FILES.getlist("file")
        if not files:
            return Response(
                {"error": "No files uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )

        saved = []
        try:
            for file in files:
                name = file.name

                if name.endswith(".rar"):
                    return Response(
                        {
                            "error": "RAR files are not supported. Please upload ZIP or SQLite files."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

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
                                    {
                                        "error": f"Invalid file name in zip: {extracted_file}"
                                    },
                                    status=status.HTTP_400_BAD_REQUEST,
                                )

                            safe_name = get_valid_filename(base_name)
                            with zip_ref.open(extracted_file) as f:
                                django_file = File(f, name=safe_name)
                                saved.append(
                                    save_to_model(django_file, safe_name, user)
                                )

                else:
                    if not is_valid_sqlite(name):
                        return Response(
                            {
                                "error": f"Invalid file type `{name}`. Only SQLite files allowed."
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    if (
                        re.search(r"[\\/]", name)
                        or name.startswith(".")
                        or not name.isascii()
                    ):
                        return Response(
                            {"error": f"Invalid file name `{name}`."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    safe_name = get_valid_filename(name)
                    saved.append(save_to_model(file, safe_name, user))

            if not saved:
                return Response(
                    {"error": "No valid SQLite files found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_files = Files.objects.filter(user=user)
            sql_file_paths = {
                f.database: f.file.path
                for f in user_files
                if f.file and os.path.isfile(f.file.path)
            }
            sql_file_paths_json = json.dumps(sql_file_paths, ensure_ascii=False)

            schema_dir = os.path.join(settings.MEDIA_ROOT, str(user.id), "schema")
            os.makedirs(schema_dir, exist_ok=True)
            print("SQL file paths:", sql_file_paths)
            print("Schema dir:", schema_dir)

            schema_builder.build_schema_ab(sql_file_paths_json, schema_dir)
            schema_builder.build_schema_c(sql_file_paths_json, schema_dir)

            # After successful import, update storage cache so frontend can sync immediately
            try:
                today = timezone.now().date()
                # get_or_create can race under SQLite when two threads try to create the same row.
                # Defensively handle UNIQUE constraint by retrying a plain get on IntegrityError.
                try:
                    du, _ = DailyUsage.objects.get_or_create(
                        user=user, date=today, defaults={"chats_used": 0}
                    )
                except IntegrityError:
                    du = DailyUsage.objects.get(user=user, date=today)
                cache_key = f"usage_cache:{user.id}"
                # compute used bytes and expose only GB values for storage
                agg = Files.objects.filter(user=user).aggregate(total=Sum("size"))
                used_bytes = int(agg.get("total") or 0)
                GB = 1024**3
                used_gb = round(used_bytes / GB, 3)
                limits, _ = UserLimits.objects.get_or_create(user=user)
                payload = {
                    "max_gb": float(limits.max_gb_db),
                    "used_gb": float(used_gb),
                }
                from django.core.cache import cache as _cache

                try:
                    _cache.set(cache_key, payload, 60)
                except Exception:
                    pass
            except Exception:
                payload = None

            response_body = {"saved": saved}
            if payload:
                # storage endpoints return a compact storage payload
                response_body["storage"] = payload

            return Response(response_body, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"])
    def add_spider_databases(self, request, *args, **kwargs):
        """Upload all Spider databases from /data/spider_data/test_database"""
        user = request.user
        spider_data_path = "/data/spider_data/test_database"

        if not os.path.exists(spider_data_path):
            return Response(
                {
                    "error": "Spider databases not found. Please ensure /data/spider_data/test_database exists."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        saved = []
        try:
            # Find all SQLite files in the Spider data directory
            sqlite_files = []
            for root, dirs, files in os.walk(spider_data_path):
                for file in files:
                    if is_valid_sqlite(file):
                        file_path = os.path.join(root, file)
                        sqlite_files.append((file, file_path))

            if not sqlite_files:
                return Response(
                    {"error": "No SQLite databases found in Spider data directory."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Upload each SQLite file
            for filename, file_path in sqlite_files:
                try:
                    with open(file_path, "rb") as f:
                        django_file = File(f, name=filename)
                        safe_name = get_valid_filename(filename)
                        saved.append(save_to_model(django_file, safe_name, user))
                except Exception as e:
                    print(f"Error uploading {filename}: {str(e)}")
                    continue

            if not saved:
                return Response(
                    {"error": "Failed to upload any Spider databases."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Generate schemas for all uploaded databases
            user_files = Files.objects.filter(user=user)
            sql_file_paths = {
                f.database: f.file.path
                for f in user_files
                if f.file and os.path.isfile(f.file.path)
            }
            sql_file_paths_json = json.dumps(sql_file_paths, ensure_ascii=False)

            schema_dir = os.path.join(settings.MEDIA_ROOT, str(user.id), "schema")
            os.makedirs(schema_dir, exist_ok=True)
            print("SQL file paths:", sql_file_paths)
            print("Schema dir:", schema_dir)

            schema_builder.build_schema_ab(sql_file_paths_json, schema_dir)
            schema_builder.build_schema_c(sql_file_paths_json, schema_dir)

            # Update storage cache
            try:
                today = timezone.now().date()
                try:
                    du, _ = DailyUsage.objects.get_or_create(
                        user=user, date=today, defaults={"chats_used": 0}
                    )
                except IntegrityError:
                    du = DailyUsage.objects.get(user=user, date=today)
                cache_key = f"usage_cache:{user.id}"
                agg = Files.objects.filter(user=user).aggregate(total=Sum("size"))
                used_bytes = int(agg.get("total") or 0)
                GB = 1024**3
                used_gb = round(used_bytes / GB, 3)
                limits, _ = UserLimits.objects.get_or_create(user=user)
                payload = {
                    "max_gb": float(limits.max_gb_db),
                    "used_gb": float(used_gb),
                }
                from django.core.cache import cache as _cache

                try:
                    _cache.set(cache_key, payload, 60)
                except Exception:
                    pass
            except Exception:
                payload = None

            response_body = {
                "saved": saved,
                "count": len(saved),
                "message": f"Successfully uploaded {len(saved)} Spider databases",
            }
            if payload:
                response_body["storage"] = payload

            return Response(response_body, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["delete"])
    def clear(self, request, *args, **kwargs):
        user = request.user
        try:
            files = Files.objects.filter(user=user)
            for f in files:
                if f.file and f.file.path and os.path.isfile(f.file.path):
                    os.remove(f.file.path)
            files.delete()
            # update usage cache after clearing
            try:
                today = timezone.now().date()
                try:
                    du, _ = DailyUsage.objects.get_or_create(
                        user=user, date=today, defaults={"chats_used": 0}
                    )
                except IntegrityError:
                    du = DailyUsage.objects.get(user=user, date=today)
                agg = Files.objects.filter(user=user).aggregate(total=Sum("size"))
                used_bytes = int(agg.get("total") or 0)
                GB = 1024**3
                limits, _ = UserLimits.objects.get_or_create(user=user)
                now = timezone.now()
                next_day = (now + timezone.timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                seconds_until_reset = int((next_day - now).total_seconds())
                payload = {
                    "max_chats": limits.max_chats,
                    "max_gb": limits.max_gb_db,
                    "chats_used_today": du.chats_used,
                    "used_bytes": used_bytes,
                    "max_bytes": int(limits.max_gb_db) * GB,
                    "seconds_until_reset": seconds_until_reset,
                }
                from django.core.cache import cache as _cache

                try:
                    _cache.set(f"usage_cache:{user.id}", payload, 60)
                except Exception:
                    pass
            except Exception:
                payload = None

            resp = {"status": "All files deleted."}
            if payload:
                resp["storage"] = payload
            return Response(resp, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        file_obj = self.get_object()
        if file_obj.user != request.user:
            return Response({"error": "Forbidden"}, status=403)
        if not file_obj.file or not os.path.exists(file_obj.file.path):
            return Response({"error": "File not found"}, status=404)
        return FileResponse(
            open(file_obj.file.path, "rb"),
            as_attachment=True,
            filename=os.path.basename(file_obj.file.name),
        )

    @action(detail=False, methods=["get"])
    def storage(self, request):
        """Return a compact storage payload: { max_gb, used_gb }"""
        user = request.user
        try:
            agg = Files.objects.filter(user=user).aggregate(total=Sum("size"))
            used_bytes = int(agg.get("total") or 0)
            GB = 1024**3
            used_gb = round(used_bytes / GB, 3)
            limits, _ = UserLimits.objects.get_or_create(user=user)
            payload = {
                "max_gb": float(limits.max_gb_db),
                "used_gb": float(used_gb),
            }
            return Response(payload, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def destroy(self, request, *args, **kwargs):
        """Override destroy to return compact storage payload after deletion."""
        instance = self.get_object()
        user = request.user
        try:
            # Delete file from disk then DB
            if (
                instance.file
                and instance.file.path
                and os.path.exists(instance.file.path)
            ):
                os.remove(instance.file.path)
            instance.delete()

            # compute storage payload
            agg = Files.objects.filter(user=user).aggregate(total=Sum("size"))
            used_bytes = int(agg.get("total") or 0)
            GB = 1024**3
            used_gb = round(used_bytes / GB, 3)
            limits, _ = UserLimits.objects.get_or_create(user=user)
            payload = {
                "max_gb": float(limits.max_gb_db),
                "used_gb": float(used_gb),
            }

            resp = {"status": "deleted", "storage": payload}
            return Response(resp, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
