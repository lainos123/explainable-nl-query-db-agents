@echo off
echo Running Django resetting...

cd backend

:: Activate virtualenv
call venv\Scripts\activate.bat

:: Remove migrations and old database
rmdir /s /q core\migrations
del db.sqlite3

:: Recreate migrations and apply them
python manage.py makemigrations core
python manage.py migrate

:: Create superuser
python manage.py createsuperuser

pause
