:: Install backend dependencies
cd backend
python -m venv venv
call venv\Scripts\python.exe -m pip install --upgrade pip
call venv\Scripts\pip.exe install -r requirements.txt
cd ..

:: Install frontend dependencies
cd frontend
npm install
cd ..

echo All dependencies installed.
pause
