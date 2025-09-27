@echo off
REM start_servers.bat
REM This script allows you to choose to start:
REM   - both frontend and backend
REM   - frontend only
REM   - backend only

echo =====================================================
echo Start Servers Menu
echo =====================================================
echo Please choose an option:
echo   1. All       - Start both frontend and backend
echo   2. Frontend  - Start frontend only
echo   3. Backend   - Start backend only
echo.

set /p choice=Enter your choice (1 / 2 / 3): 

if "%choice%"=="1" (
    echo Starting frontend on port 8000...
    start cmd /k "cd frontend && npm run dev -- -p 8000 --turbopack"

    echo Starting backend on port 8001...
    start cmd /k "cd backend && call venv\Scripts\python.exe -m uvicorn backend.asgi:application --host 127.0.0.1 --port 8001"

    echo Opening browser windows...
    start http://localhost:8001/admin/
    start http://localhost:8000
    goto end
)

if "%choice%"=="2" (
    echo Starting frontend on port 8000...
    start cmd /k "cd frontend && npm run dev -- -p 8000 --turbopack"

    echo Opening browser window for frontend...
    start http://localhost:8000
    goto end
)

if "%choice%"=="3" (
    echo Starting backend on port 8001...
    start cmd /k "cd backend && call venv\Scripts\python.exe -m uvicorn backend.asgi:application --host 127.0.0.1 --port 8001"

    echo Opening browser window for backend admin interface...
    start http://localhost:8001/admin/
    goto end
)

echo Invalid choice: "%choice%". Please run the script again and enter 1, 2, or 3.

:end
