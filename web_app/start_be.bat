:: Run backend Django in port 8081
start cmd /k "cd backend && call venv\Scripts\python.exe -m uvicorn backend.asgi:application --host 127.0.0.1 --port 8001"
