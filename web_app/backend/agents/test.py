import os
import json
import django
from datetime import datetime, timezone

# ===== Django setup =====
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # replace with your settings module
django.setup()

from django.contrib.auth import get_user_model
from core.models import APIKeys
from langchain_openai import ChatOpenAI

# Save log file alongside this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "test_log.txt")


def log_write(text: str):
    """Append both to console and log file."""
    print(text)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")


# ====== Monkey patch to log prompts ======
_orig_invoke = ChatOpenAI.invoke


def debug_invoke(self, input, *args, **kwargs):
    log_write("\n=== PROMPT SENT TO LLM ===")
    try:
        if isinstance(input, dict):
            log_write(json.dumps(input, indent=4, ensure_ascii=False))
        else:
            log_write(str(input))
    except Exception as e:
        log_write(f"[DEBUG] Could not serialize prompt: {e}")
        log_write(repr(input))
    log_write("=== END PROMPT ===\n")
    return _orig_invoke(self, input, *args, **kwargs)


ChatOpenAI.invoke = debug_invoke
# =========================================

# Import agents after patch
from agents.a_db_select import run as run_agent_a
from agents.b_table_select import run as run_agent_b
from agents.c_sql_generate import run as run_agent_c
from utils import sql_connector  # Agent D


def get_api_key_for_user(username: str, password: str):
    """Authenticate user and fetch stored API key from DB"""
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        if not user.check_password(password):
            raise ValueError("Invalid password")
    except User.DoesNotExist:
        raise ValueError("User not found")

    try:
        return user.id, APIKeys.objects.get(user=user).api_key
    except APIKeys.DoesNotExist:
        raise ValueError("API key not found for this user")


def main():
    # change these to the Django account you want to test with
    username = "admin"
    password = "admin123"

    user_id, api_key = get_api_key_for_user(username, password)

    # append a new run header instead of replacing
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"=== Test Run {datetime.now(timezone.utc).isoformat()} ===\n")

    # === get query from user ===
    query = input("Enter your natural language query: ").strip()
    if not query:
        log_write("No query entered. Exiting.")
        return

    log_write(f"\nRunning pipeline for user_id={user_id}, username={username}")
    log_write(f"User query: {query}\n")

    log_write(">>> Agent A")
    out_a = run_agent_a(api_key, {"query": query}, user_id)
    log_write("Output A:\n" + json.dumps(out_a, indent=4, ensure_ascii=False))

    log_write("\n>>> Agent B")
    out_b = run_agent_b(api_key, out_a, user_id)
    log_write("Output B:\n" + json.dumps(out_b, indent=4, ensure_ascii=False))

    log_write("\n>>> Agent C")
    out_c = run_agent_c(api_key, out_b, user_id)
    log_write("Output C:\n" + json.dumps(out_c, indent=4, ensure_ascii=False))

    log_write("\n>>> Agent D (SQL execution)")
    try:
        out_d = sql_connector.run_sql(api_key, out_c, user_id)
        log_write("Output D:\n" + json.dumps(out_d, indent=4, ensure_ascii=False))
    except Exception as e:
        log_write(f"Agent D failed: {e}")


if __name__ == "__main__":
    main()
