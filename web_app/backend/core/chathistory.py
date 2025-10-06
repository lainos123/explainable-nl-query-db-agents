import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


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
