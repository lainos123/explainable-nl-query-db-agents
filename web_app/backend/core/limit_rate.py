from rest_framework.response import Response
from rest_framework import status
from .models import DailyUsage

from django.utils import timezone
from django.db.models import Sum
from .models import Files, UserLimits
import zipfile
import os

def can_user_chat(user):
    # Deprecated: use has_chat_quota / increment_user_chats for clearer semantics.
    today = timezone.now().date()
    usage, _ = DailyUsage.objects.get_or_create(user=user, date=today)
    try:
        limits = user.userlimits
        max_chats = getattr(limits, 'max_chats', 0)
    except UserLimits.DoesNotExist:
        max_chats = 0

    return usage.chats_used < max_chats


def has_chat_quota(user) -> bool:
    """Return True if user has quota left for today's chats (does not mutate state)."""
    today = timezone.now().date()
    usage, _ = DailyUsage.objects.get_or_create(user=user, date=today)
    try:
        limits = user.userlimits
        max_chats = getattr(limits, 'max_chats', 0)
    except UserLimits.DoesNotExist:
        max_chats = 0
    return usage.chats_used < max_chats


def increment_user_chats(user, amount: int = 1):
    """Atomically increment the user's chats_used counter for today by `amount`.
    Safe against race conditions; returns the new value or None on failure."""
    from django.db.models import F
    today = timezone.now().date()
    try:
        du, created = DailyUsage.objects.get_or_create(user=user, date=today, defaults={'chats_used': 0})
    except Exception:
        # Fallback to get after create race
        du = DailyUsage.objects.get(user=user, date=today)
    try:
        DailyUsage.objects.filter(pk=du.pk).update(chats_used=F('chats_used') + amount)
        du.refresh_from_db()
        return du.chats_used
    except Exception:
        try:
            du.chats_used = du.chats_used + amount
            du.save(update_fields=['chats_used'])
            return du.chats_used
        except Exception:
            return None


class ChatLimitMixin:
    # Override dispatch to include rate limiting logic

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated and if the request method is POST
        if request.user.is_authenticated and request.method.lower() in ["post"]:
            if not can_user_chat(request.user):
                return Response(
                    {"error": "Daily chat limit reached."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
        return super().dispatch(request, *args, **kwargs)

class GBLimitMixin:
    # Scan uploaded + current files to ensure user is within their GB limit
    # Behaviour:
    # 1) Query the DB to sum already-uploaded file sizes for the user (server scan).
    # 2) Inspect incoming files in `request.FILES` to compute the uploaded size (input scan).
    # 3) Compare (existing + incoming) against `user.userlimits.max_gb_db`.
    # If over the limit, reject the request before it reaches the view.

    GB = 1024 ** 3

    def _user_current_bytes(self, user):
        """Return total bytes already stored for `user` by summing Files.size."""
        agg = Files.objects.filter(user=user).aggregate(total=Sum('size'))
        total = agg.get('total') or 0
        return int(total)

    def _incoming_files_bytes(self, request):
        """Return total bytes of files included in the current request (if any)."""
        files = request.FILES.getlist('file') if hasattr(request, 'FILES') else []
        total = 0
        # helper for recognising sqlite extensions
        SQLITE_EXTENSIONS = {'.sqlite'} | {f'.sqlite{i}' for i in range(7)}

        for f in files:
            try:
                name = getattr(f, 'name', '') or ''
                lname = name.lower()
                if lname.endswith('.zip'):
                    # Sum the uncompressed sizes of valid sqlite entries in the zip
                    try:
                        z = zipfile.ZipFile(f)
                        for info in z.infolist():
                            if info.is_dir():
                                continue
                            _, ext = os.path.splitext(info.filename)
                            if ext.lower() in SQLITE_EXTENSIONS:
                                total += int(info.file_size or 0)
                        z.close()
                        continue
                    except Exception:
                        # Fallback to the uploaded zip size if zip can't be read
                        pass

                # Django's UploadedFile exposes a `size` attribute
                total += int(getattr(f, 'size', 0) or 0)
            except Exception:
                # If size can't be determined, assume 0 to be safe
                continue
        return total

    def dispatch(self, request, *args, **kwargs):
        # Only check for authenticated users on data-changing requests
        if request.user.is_authenticated and request.method.lower() in ["post", "put", "patch"]:
            # Ensure user has limits
            try:
                limits = request.user.userlimits
                max_gb = getattr(limits, 'max_gb_db', 0)
            except UserLimits.DoesNotExist:
                # If no limits, default to 0 GB to avoid accidental overuse
                max_gb = 0

            max_bytes = int(max_gb) * self.GB

            current = self._user_current_bytes(request.user)
            incoming = self._incoming_files_bytes(request)

            if current + incoming > max_bytes:
                # If the limit is exceeded, return an informative error
                return Response(
                    {
                        "error": "Storage quota exceeded.",
                        "details": {
                            "max_gb": max_gb,
                            "current_bytes": current,
                            "incoming_bytes": incoming,
                        },
                    },
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )

        # Fall back to normal dispatch
        return super().dispatch(request, *args, **kwargs)