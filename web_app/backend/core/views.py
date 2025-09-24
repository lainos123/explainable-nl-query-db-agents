import json
import re
import os, zipfile

from django.core.files import File
from django.utils.text import get_valid_filename
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from django.http import FileResponse

from utils import schema_builder

from django.utils import timezone
from datetime import date

from .models import Files, APIKeys, DailyUsage, UserLimits
from .models import Chats
from .limit_rate import GBLimitMixin
from .serializers import FilesSerializer, APIKeysSerializer
from rest_framework.views import APIView
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

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
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

                            safe_name = get_valid_filename(base_name)
                            with zip_ref.open(extracted_file) as f:
                                django_file = File(f, name=safe_name)
                                saved.append(save_to_model(django_file, safe_name, user))

                else:
                    if not is_valid_sqlite(name):
                        return Response(
                            {"error": f"Invalid file type `{name}`. Only SQLite files allowed."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    if re.search(r"[\\/]", name) or name.startswith(".") or not name.isascii():
                        return Response({"error": f"Invalid file name `{name}`."}, status=status.HTTP_400_BAD_REQUEST)

                    safe_name = get_valid_filename(name)
                    saved.append(save_to_model(file, safe_name, user))

            if not saved:
                return Response({"error": "No valid SQLite files found."}, status=status.HTTP_400_BAD_REQUEST)

            user_files = Files.objects.filter(user=user)
            sql_file_paths = {
                f.database: f.file.path
                for f in user_files if f.file and os.path.isfile(f.file.path)
            }
            sql_file_paths_json = json.dumps(sql_file_paths, ensure_ascii=False)

            schema_dir = os.path.join(settings.MEDIA_ROOT, str(user.id), "schema")
            os.makedirs(schema_dir, exist_ok=True)
            print("SQL file paths:", sql_file_paths)
            print("Schema dir:", schema_dir)

            schema_builder.build_schema_ab(sql_file_paths_json, schema_dir)
            schema_builder.build_schema_c(sql_file_paths_json, schema_dir)

            # After successful import, update usage cache so frontend can sync immediately
            try:
                today = timezone.now().date()
                du, _ = DailyUsage.objects.get_or_create(user=user, date=today, defaults={'chats_used': 0})
                cache_key = f"usage_cache:{user.id}"
                # compute used bytes and other fields for a best-effort payload
                agg = Files.objects.filter(user=user).aggregate(total=Sum('size'))
                used_bytes = int(agg.get('total') or 0)
                GB = 1024 ** 3
                limits, _ = UserLimits.objects.get_or_create(user=user)
                now = timezone.now()
                next_day = (now + timezone.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                seconds_until_reset = int((next_day - now).total_seconds())
                payload = {
                    'max_chats': limits.max_chats,
                    'max_gb': limits.max_gb_db,
                    'chats_used_today': du.chats_used,
                    'used_bytes': used_bytes,
                    'max_bytes': int(limits.max_gb_db) * GB,
                    'seconds_until_reset': seconds_until_reset,
                }
                from django.core.cache import cache as _cache
                try:
                    _cache.set(cache_key, payload, 60)
                except Exception:
                    pass
            except Exception:
                payload = None

            response_body = {'saved': saved}
            if payload:
                response_body['usage'] = payload

            return Response(response_body, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                du, _ = DailyUsage.objects.get_or_create(user=user, date=today, defaults={'chats_used': 0})
                agg = Files.objects.filter(user=user).aggregate(total=Sum('size'))
                used_bytes = int(agg.get('total') or 0)
                GB = 1024 ** 3
                limits, _ = UserLimits.objects.get_or_create(user=user)
                now = timezone.now()
                next_day = (now + timezone.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                seconds_until_reset = int((next_day - now).total_seconds())
                payload = {
                    'max_chats': limits.max_chats,
                    'max_gb': limits.max_gb_db,
                    'chats_used_today': du.chats_used,
                    'used_bytes': used_bytes,
                    'max_bytes': int(limits.max_gb_db) * GB,
                    'seconds_until_reset': seconds_until_reset,
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
                resp['usage'] = payload
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
            filename=os.path.basename(file_obj.file.name)
        )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def download_chat_markdown(request):
    """
    Accepts JSON POST { messages: [{id, sender, text, createdAt}, ...], filename?: str }
    Returns a markdown attachment representing the chat history.
    """
    try:
        data = request.data
        messages = data.get("messages", [])
        filename = data.get("filename") or "chat_history.md"
        # build markdown
        lines = ["# Chat history\n"]
        for m in messages:
            ts = m.get("createdAt")
            sender = m.get("sender", "user")
            text = m.get("text", "")
            # simple timestamp formatting if numeric
            if isinstance(ts, (int, float)):
                try:
                    import datetime
                    ts_str = datetime.datetime.fromtimestamp(ts/1000).isoformat()
                except Exception:
                    ts_str = str(ts)
            else:
                ts_str = str(ts)
            lines.append(f"**{sender}** - {ts_str}\n\n")
            lines.append(text + "\n\n---\n\n")

        content = "".join(lines)
        from django.http import HttpResponse
        resp = HttpResponse(content, content_type="text/markdown")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp
    except Exception as e:
        return Response({"error": str(e)}, status=500)

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


class UsageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Ensure default related rows exist (defensive for older users)
        limits, _ = UserLimits.objects.get_or_create(user=user)
        max_chats = limits.max_chats
        max_gb = limits.max_gb_db

        # today's chats used; create row if missing
        today = timezone.now().date()
        usage_obj, _ = DailyUsage.objects.get_or_create(user=user, date=today, defaults={"chats_used": 0})
        chats_used = usage_obj.chats_used

        # used bytes on server
        agg = Files.objects.filter(user=user).aggregate(total=Sum('size'))
        used_bytes = int(agg.get('total') or 0)

        GB = 1024 ** 3
        # compute next reset at next midnight (server tz)
        now = timezone.now()
        # start of next day
        next_day = (now + timezone.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_until_reset = int((next_day - now).total_seconds())

        return Response(
            {
                "max_chats": max_chats,
                "max_gb": max_gb,
                "chats_used_today": chats_used,
                "used_bytes": used_bytes,
                "max_bytes": int(max_gb) * GB,
                "server_time": now,
                "reset_time": next_day,
                "seconds_until_reset": seconds_until_reset,
            }
        )


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def chats_view(request):
    """GET: return saved chat messages for the current user
       POST: accept JSON { messages: [...] } and save into Chats model
       DELETE: remove saved chat history for user
    """
    try:
        user = request.user
        if request.method == "GET":
            try:
                obj = Chats.objects.get(user=user)
                data = obj.chats
                try:
                    parsed = json.loads(data) if data else []
                except Exception:
                    parsed = []
                return Response({"messages": parsed}, status=200)
            except Chats.DoesNotExist:
                return Response({"messages": []}, status=200)

        if request.method == "POST":
            msgs = request.data.get("messages")
            if msgs is None:
                return Response({"error": "Missing messages"}, status=400)
            obj, _ = Chats.objects.get_or_create(user=user)
            obj.chats = json.dumps(msgs, ensure_ascii=False)
            obj.save(update_fields=["chats"])
            return Response({"status": "saved"}, status=200)

        if request.method == "DELETE":
            Chats.objects.filter(user=user).delete()
            return Response({"status": "deleted"}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
