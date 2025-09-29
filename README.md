# Explainable Natural Language Query Interface for Relational Databases Using a Multi-Agent System
For CITS5553 - Data Science Capstone Project | Semester 2, 2025

## Setup & Running the Application (Docker Only)

This project is designed to be run entirely using Docker. No manual Python or Conda environment setup is required.


### 1. Download the Spider Database Dataset

To use the "Add All Spider" feature and test the system with comprehensive databases, you **must manually download** the Spider dataset and place it in the correct directory.

**Steps:**

1. **Download the Spider dataset:**
   - Visit the official Spider dataset page: https://yale-lily.github.io/spider/
   - Or use the direct Google Drive link: [https://drive.google.com/file/d/1403EGqzIDoHMdQF4c9Bkyl7dZLZ5Wt6J/view](https://drive.google.com/file/d/1403EGqzIDoHMdQF4c9Bkyl7dZLZ5Wt6J/view)
   - Download the dataset ZIP file to your computer.

2. **Extract and place the dataset:**
   - Unzip the downloaded file. It should be called `spider_data`
   - Move or copy this folder to `data` folder so we should have `data/spider/data`

   Your directory structure should look like:
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

**Note:** The Spider databases are not included in this Git repository due to size constraints, but they are essential for testing the full functionality of the system. Each team member must perform this manual download and placement step on their own machine.

---

## Docker Setup

For easy deployment and testing, we provide Docker configuration:

1. **Navigate to the web application directory:**
   ```bash
   cd web_app
   ```

2. **Start the application with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Django Admin: http://localhost:8000/admin

4. **Set up your OpenAI API Key:**
   - Login to the web application
   - Click the "Settings (API Key)" button in the menu
   - Enter your OpenAI API key (get one from https://platform.openai.com/account/api-keys)
   - Save your API key

5. **Use the "Add All Spider" feature:**
   - After downloading and placing the Spider datasets as described above
   - Go to the Files section
   - Click the purple "Add All Spider" button
   - This will automatically upload all 200+ Spider databases and generate their schemas

6. **Test the agents:**
   - Go to the chatbot and ask questions about your databases
   - The AI agents will use your API key to generate SQL queries

**Note**: Each user needs their own OpenAI API key. The `.env` file API key is only used for development/testing.

The Docker setup automatically mounts the `../data` directory, so your Spider databases will be accessible to the backend container.