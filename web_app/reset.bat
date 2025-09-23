echo Running Django resetting...
cd backend

:: Remove migrations and old database
rmdir /s /q core\migrations
del db.sqlite3

:: Recreate migrations and apply them
call venv\Scripts\python.exe manage.py makemigrations core
call venv\Scripts\python.exe manage.py migrate

:: Create superuser
call venv\Scripts\python.exe manage.py createsuperuser

pause
