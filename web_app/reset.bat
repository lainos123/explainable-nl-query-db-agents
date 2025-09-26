@echo off
echo Running Django resetting...
cd backend

:: Remove __pycache__ directories if present
for /d /r %%d in (__pycache__) do (
  rmdir /s /q "%%d"
  echo Removed %%d
)

:: Remove __init__.py files in migrations folders if present
for /r core\migrations %%f in (__init__.py) do (
  del "%%f"
  echo Removed %%f
)

:: Remove migrations if present
if exist core\migrations (
  rmdir /s /q core\migrations
  echo core\migrations removed
) else (
  echo No migrations to remove
)

:: Remove media if present
if exist media (
  rmdir /s /q media
  echo media folder removed
) else (
  echo No media to remove
)

:: Remove SQLite database if present
if exist db.sqlite3 (
  del db.sqlite3
  echo db.sqlite3 removed
) else (
  echo No database to remove
)

:: Recreate migrations and apply them
call venv\Scripts\python.exe manage.py makemigrations core
call venv\Scripts\python.exe manage.py migrate

:: Create superuser
call venv\Scripts\python.exe manage.py createsuperuser

pause
