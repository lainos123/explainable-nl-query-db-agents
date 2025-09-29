import json
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Sum

from .models import APIKeys, DailyUsage, UserLimits, Chats, Files
from .serializers import APIKeysSerializer


class APIKeysViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, _ = APIKeys.objects.get_or_create(user=self.request.user)
        return obj

    def list(self, request):
        """GET: return masked API key info"""
        obj = self.get_object()
        serializer = APIKeysSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        obj = self.get_object()
        new_value = request.data.get("api_key", "")
        obj.api_key = new_value
        obj.save(update_fields=["api_key"])
        # Do NOT return the raw API key. Return only has_key flag.
        serializer = APIKeysSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        # full update (PUT) - same behavior as create for this one-field model
        return self.create(request)

    def partial_update(self, request, pk=None):
        # PATCH
        return self.create(request)


class UsageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Ensure default related rows exist (defensive for older users)
        limits, _ = UserLimits.objects.get_or_create(user=user)
        max_chats = limits.max_chats
        max_gb = limits.max_gb_db

        # today's chats used; do NOT create a row on a read. If the row is missing, report 0.
        today = timezone.now().date()
        try:
            usage_obj = DailyUsage.objects.get(user=user, date=today)
            chats_used = usage_obj.chats_used
        except DailyUsage.DoesNotExist:
            chats_used = 0

        # used bytes on server
        agg = Files.objects.filter(user=user).aggregate(total=Sum("size"))
        used_bytes = int(agg.get("total") or 0)

        GB = 1024**3
        # compute next reset at next midnight (server tz)
        now = timezone.now()
        # start of next day
        next_day = (now + timezone.timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        seconds_until_reset = int((next_day - now).total_seconds())

        # Return a minimal response containing only chat-usage related fields.
        return Response(
            {
                "max_chats": max_chats,
                "chats_used_today": chats_used,
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
