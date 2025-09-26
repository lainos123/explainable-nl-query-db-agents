@echo on
:: Install backend dependencies
cd backend
:: Remove existing virtual environment if it exists
if exist venv rmdir /s /q venv
python -m venv venv
call venv\Scripts\python.exe -m pip install --upgrade pip
call venv\Scripts\pip.exe install -r requirements.txt
cd ..

:: Install frontend dependencies
cd frontend
npm install
cd ..
pause
echo All dependencies installed.
pause