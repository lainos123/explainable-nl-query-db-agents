@echo off
:: Install backend dependencies
cd backend
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..\..

:: Install frontend dependencies
cd frontend
npm install
cd ..\..

echo All dependencies installed.
pause
