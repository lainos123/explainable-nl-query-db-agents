@echo off
REM re_load_after_new_ver.bat
REM Usage: double-click or run from PowerShell/CMD at the project root.
REM This script updates frontend deps, builds the frontend, updates backend Python deps (using venv if present), runs migrations and collects static files.

SETLOCAL ENABLEDELAYEDEXPANSION
cd /d "%~dp0"
echo === Reload after new version: starting ===

necho [1/4] Frontend: npm install, npm update, npm run build
if exist "frontend\package.json" (
  pushd frontend
  echo Working directory: %CD%
  echo Running: npm install
  call npm install
  echo Running: npm update
  call npm update
  echo Running: npm run build
  call npm run build
  popd
) else (
  echo Skipping frontend: frontend\package.json not found
)

necho.
echo [2/4] Backend: using local venv python if available, else system python
set PYTHON=
if exist "backend\venv\Scripts\python.exe" (
  set PYTHON=backend\venv\Scripts\python.exe
) else if exist "venv\Scripts\python.exe" (
  set PYTHON=venv\Scripts\python.exe
) else (
  set PYTHON=python
)
echo Using Python: %PYTHON%

 if exist "backend\manage.py" (
  echo Upgrading pip...
  call "%PYTHON%" -m pip install -U pip
  if exist "backend\requirements.txt" (
    echo Installing backend requirements...
    call "%PYTHON%" -m pip install -r backend\requirements.txt
  ) else (
    echo No backend\requirements.txt found, skipping pip install
  )
  echo Running Django migrations...
  call "%PYTHON%" backend\manage.py migrate --noinput
  echo Collecting static files...
  call "%PYTHON%" backend\manage.py collectstatic --noinput
) else (
  echo Skipping backend steps: backend\manage.py not found
)

necho.
echo [3/4] Optional: restart backend/frontend servers
echo If you want the script to start servers, run start_be.bat and start_fe.bat or start.bat manually.

necho.
echo === Reload complete ===
ENDLOCAL
pause
