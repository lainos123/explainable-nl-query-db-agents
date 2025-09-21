@echo off
:: Run frontend Next.js in port 8000
start cmd /k "cd frontend && npm run dev -- -p 8000 --turbopack"

:: Run backend Django in port 8001
start cmd /k "cd backend && call venv\Scripts\activate && python manage.py runserver 8001"


:: Open the browser to the frontend
start http://localhost:8000
:: Open the browser to the backend admin interface
start http://localhost:8001/admin/