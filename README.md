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
  bb