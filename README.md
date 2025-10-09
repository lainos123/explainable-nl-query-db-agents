# Explainable Natural Language Query Interface for Relational Databases Using a Multi-Agent System

For CITS5553 - Data Science Capstone Project | Semester 2, 2025

---

<p align="center">
  <img src="media/demo.png" alt="Demo Screenshot" width="700"/>
</p>

---

## I. Project Overview

This project implements an explainable natural language query interface for relational databases using a multi-agent system. It allows users to interact with databases by asking questions in natural language, and the system generates SQL queries to retrieve the relevant data. The key features include:

- **Multi-Agent System:** Utilizes multiple AI agents to handle different aspects of the query process, including understanding the question, generating SQL, executing the query, and explaining the results.
- **Explainability:** Provides explanations for the generated SQL queries and the results, enhancing user trust and understanding.
- **Database Support:** Supports multiple SQLite databases, including the Spider dataset, allowing users to query various database schemas.
- **User-Friendly Interface:** A web-based frontend built with Next.js for easy interaction.
- **Backend:** A Django REST API backend to manage database interactions and agent coordination.
- **Dockerized Deployment:** The entire application can be run using Docker, simplifying setup and deployment.

**The architecture of the system is illustrated below:**


![alt text](<Diagram 01.jpg>)


## II. Setup Guide

This project is designed to be run entirely using Docker. No manual Python or Conda environment setup is required.

Before starting, if you use Windows, ensure that you have run the code below in your terminal to avoid line ending issues (CRLF bug of Windows).

```bash
git config --global core.autocrlf input
```

### 1. Download and Prepare the Spider Dataset

- **Download the Spider Dataset:**
  - Visit: https://yale-lily.github.io/spider  
    or use the direct link: [Google Drive Download](https://drive.google.com/file/d/1403EGqzIDoHMdQF4c9Bkyl7dZLZ5Wt6J/view)
  - Download the ZIP file to your computer.

- **Extract and Place the Dataset for default databases feature:**

  - This is can be skipped if you want to use your own databases only, but `Add All Spider` feature will be disabled if you do so.
  - Unzip the file. The folder should be named `spider_data`.
  - Inside `spider_data`, there is a subfolder named `test_database` containing 200+ SQLite databases, which is the whole dataset. 
  - Delete all unnecessary files especially the `database` folder as it is a duplicate train dataset of `test_database` and only left with `test_database` as the tree structure shown below.
  - Move or copy this folder into the `data` directory at the root of this project, so you have: `data/spider_data`

  Your directory should look like:
  ```
  data/
  └── spider_data/
      └── test_database/
          ├── academic/
          │   ├── academic.sqlite
          │   └── schema.sql
          ├── flight_1/
          │   ├── flight_1.sqlite
          │   └── schema.sql
          ├── car_1/
          │   ├── car_1.sqlite
          │   └── schema.sql
          └── ... (200+ more databases)
  ```

  > **Note:** The Spider databases are not included in this repository due to size. Each user must download and place them manually.

### 2. Install Docker

- Download Docker Desktop: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
- Install for your OS (Windows, macOS, or Linux).
- **Start Docker Desktop** and wait until it is running.

### 3. Start the Application

- Open a terminal and navigate to the web application directory:
  ```bash
  cd web_app
  ```
- Start the application with Docker Compose:
  ```bash
  docker-compose up --build
  ```
  > The first run may take a few minutes as Docker builds the images.

- The Docker setup automatically mounts the `../data` directory, so your Spider databases (if present) will be accessible to the backend.

### 4. Access the Application

- **Frontend:** [http://localhost:3001](http://localhost:3001)
- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **Django Admin:** [http://localhost:8000/admin](http://localhost:8000/admin)

### 5. Login Credentials

- **Django Admin Login (For controlling the backend server):**
  - Visit [http://localhost:8000/admin](http://localhost:8000/admin)
  - Login 
      - **Username:** `admin`
      - **Password:** `admin123`

- **Web Application Login:**
  - Log in at [http://localhost:3001](http://localhost:3001)
  - Use the same credentials (`admin` / `admin123`)

### 6. Add Your OpenAI API Key

- After logging in, click the **"API Key Settings"** button in the menu.
- Enter your OpenAI API key (get one from [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)).
- Click **Save**.

  > **Note:** Each user must enter their own OpenAI API key. The `.env` file API key is only for development/testing, currently not in use.

### 7. Add the Spider Databases or Your Own Databases

- Go to "View/Import/Delete Databases" in the menu.
- Click the purple **"Add All Spider"** button to upload all Spider databases and generate their schemas.
- Alternatively, you can upload your own SQLite databases using the **"Add"** button. The application accepts `.sqlite` files that up to version 6 (currently .sqlite3). You can zip multiple files and upload them together or upload them one by one. Ensure no duplicate database names, and no _MACOSX folders inside the zip file.
- After uploading, the databases will appear in the list and further manipulation is possible (view schema, delete, etc.).

### 8. Test the Agents

- Go to the chatbot and ask questions about your databases.
**Example question:**
> Find the name of all students who were in the tryout sorted in alphabetic order
- The AI agents will use your API key to generate SQL queries and provide explanations.
- Play with Agent Parameters

### 9. Web Servers Development

As this is a Data Science Project Application, the backend is connected with an external `data` folder so it can be readable and convenient for local usage.

However, it also prevents non-local app deployment. So, if you want to build web servers, by using docker or not, you will need to change the path of the default `spider` data to inside the `media` folder of the backend instead of the current `data` folder, which is outside of the `web_app` folder as it is now.

---

**Troubleshooting:**
If you encounter issues, ensure Docker is running and the `data/spider_data` directory exists (if using the Spider dataset).
For further help, consult your team.