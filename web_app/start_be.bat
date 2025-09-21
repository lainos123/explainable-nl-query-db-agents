@echo off
:: Run backend Django in port 8081
start cmd /k "cd backend && call venv\Scripts\activate && python manage.py runserver 8001"
