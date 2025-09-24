@echo off
REM freeze_venv_to_txt.bat
REM Detects a virtualenv (backend\venv, venv) or uses system python and writes pip freeze to backend\requirements_freeze.txt

SETLOCAL ENABLEDELAYEDEXPANSION
cd /d "%~dp0"
echo === Freeze venv packages to text ===

nset PYTHON=
if exist "backend\venv\Scripts\python.exe" (
  set PYTHON=backend\venv\Scripts\python.exe
) else if exist "venv\Scripts\python.exe" (
  set PYTHON=venv\Scripts\python.exe
) else (
  set PYTHON=python
)
echo Using Python: %PYTHON%

nset OUTFILE=backend\requirements_freeze.txt
echo Writing pip freeze to %OUTFILE%

nrem Ensure backend directory exists
if not exist "backend" mkdir backend

nrem Run pip freeze and redirect output
call "%PYTHON%" -m pip freeze > "%OUTFILE%"
if %errorlevel% neq 0 (
  echo ERROR: pip freeze failed (exit code %errorlevel%).
  echo Try activating your virtualenv or run this script from an elevated prompt.
  pause
  exit /b %errorlevel%
)

necho Successfully wrote %OUTFILE% (size:)
for %%I in (%OUTFILE%) do echo %%~zI bytes

necho === Done ===
ENDLOCAL
pause
