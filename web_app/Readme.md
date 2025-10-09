# Guide For Setting Up the Web Application Without Docker for Development Phase (Not Recommended)

You will need npm and python installed on your machine

Please run these commands in terminal to set up the project

Please make sure you are in the root directory of this app, not the whole project directory by:

```
cd Web_app
```

## 1. How to install npm and its packages

- First install nodejs from https://nodejs.org/en/download/
- Then run this command in terminal to install npm packages

```
cd frontend
npm install
```

## 2. How to install python venv and pip install its packages

- First install python from https://www.python.org/downloads/
- Then run these commands in terminal to set up python venv and install pip packages
- Make sure you are in the root directory where requirements.txt is located

```
cd backend
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
```

## 3. How to set up nextjs for frontend

**Linux**

```
npx create-next-app@latest frontend --y
cd frontend
npm run dev
```

**Windows**

```
npx create-next-app@latest frontend --yes
cd frontend
npm run dev
```

## 4. How to set up django for backend

**Linux**

```
venv/Scripts/activate
django-admin startproject backend
cd backend
```
**Windows**

```
venv/Scripts/activate.ps1
django-admin startproject backend
cd backend
```

## 5. How to run django server

- Open a terminal and make sure you are in the backend directory

```
# Change port number if needed
python manage.py runserver 8081
```
- You then can go to {URL} (e.g., http://localhost:8000) to see the backend

## 6. How to run nextjs server

- Open a new terminal and make sure you are in the frontend directory
- We use turbopack for faster performance so make sure to include `--turbopack` flag

```
npm run dev -- -p 8080 --turbopack
```

- You then can go to {URL} (e.g., http://localhost:3001) to see the frontend

## 7. How to save packages to requirements.txt (Must done everytime you install a new package)

```
pip freeze > requirements.txt
```

## 8. How to use Django after starting the server

- Admin page: Go to {URL}/admin (e.g., http://localhost:8000/admin)
- Currently, the superuser account is:
  - Username: admin
  - Password: admin123
  - Email: admin@gmail.com
- You can change the superuser account by creating a new one.

```
python manage.py createsuperuser
```

- What Django admin page can do:
  - Add, delete, and modify users
  - Add, delete, and modify chat history
  - Add, delete, and modify files
  - Add, delete, and modify user profiles
- API page: Go to {URL}/api (e.g., http://localhost:8000/api)
  - You can see all the API endpoints available for the backend
- You can test the API endpoints using tools like Postman or curl
- Example API endpoints:
    - Currently Empty
- You can also control the database in admin page (If we set up like that, but currently we  still think about it, highly chance we will set up like that)
    - You can see all the tables in the database
    - You can add, delete, and modify data in the tables
- We can put more abilities in the admin page if needed

## 9. How to use Nextjs after starting the server

- Go to {URL} (e.g., http://localhost:3001)