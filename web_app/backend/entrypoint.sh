#!/usr/bin/env bash
set -e
python manage.py migrate --noinput
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
python - <<'PYCODE'
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ["DJANGO_SUPERUSER_USERNAME"]
email = os.environ["DJANGO_SUPERUSER_EMAIL"]
password = os.environ["DJANGO_SUPERUSER_PASSWORD"]
if not User.objects.filter(username=username).exists():
User.objects.create_superuser(username=username, email=email, password=password)
print(f"Created superuser '{username}'")
else:
  print(f"Superuser '{username}' already exists")
PYCODE
else
echo "DJANGO_SUPERUSER_* env vars not all set; skipping superuser creation"
fi
exec python manage.py runserver 0.0.0.0:8000
