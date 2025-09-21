@echo off
:: Install backend dependencies from web_app folder
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
cd ..
:: Install frontend dependencies from web_app folder
cd frontend
npm install
cd ..
echo All dependencies installed.