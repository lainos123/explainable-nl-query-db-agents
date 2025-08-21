# Explainable Natural Language Query Interface for Relational Databases Using a Multi-Agent System
For CITS5553 - Data Science Capstone Project | Semester 2, 2025

## Environment Setup

We use Conda to manage our project's Python environment. Follow these steps to get started:

### 1. Install Conda
If you don't have Conda, install [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

### 2. Create & Activate the Environment
Open your terminal, navigate to the project's root folder, and run:
`conda env create -f environment.yml`

Once complete, activate the environment:

`conda activate CITS5553-Group-9`

## Repository Setup
```
.
├── agents/                         # Holds the final, production-ready code for each agent.
│   ├── __init__.py                 # A file that makes Python treat the 'agents' directory as a package.
│   ├── agent_a.py                  # A modular file for the first agent's logic (e.g., DatabaseSelector).
│   ├── agent_b.py                  # A modular file for the second agent's logic (e.g., TableColumnSelector).
│   └── agent_c.py                  # A modular file for the third agent's logic (e.g., SQLGenerator).
├── data/                           # Contains all data used in the project.
│   ├── processed/                  # For data that has been cleaned, transformed, or pre-computed.
│   │   └── embeddings/             # Specifically for pre-computed database schema embeddings.
│   ├── raw/                        # For the original, untouched source data (the Spider dataset).
│   │   └── spider_data/            # The Spider dataset, kept in its original form.
│   └── interim/                    # For intermediate data generated during processing.
├── docs/                           # Contains human-readable project documentation.
│   └── proposal/                   # A sub-directory specifically for the team's project proposal.
│       └── Group9 - Proposal - FINAL.pdf  # The official project proposal document.
├── logs/                           # All application and agent log files.
├── notebooks/                      # For exploratory data analysis (EDA), prototyping, and agent development.
│   ├── agent-development/          # Notebooks used for building and testing the logic of individual agents.
│   │   ├── agent-a-dev.ipynb       # An example notebook for developing and testing Agent A.
│   │   └── ...                     # Other agent development notebooks.
│   ├── exploratory-analysis/       # Notebooks for general data exploration and analysis.
│   └── prototyping/                # A sandbox for quick code snippets and small tests.
├── references/                     # A centralised location for all scholarly articles and research papers.
├── reports/                        # Contains all generated reports, figures, and evaluation metrics.
│   └── evaluation_reports/         # Specifically for reports on model performance and agent metrics.
├── src/                            # The main source code for the application.
│   ├── __init__.py                 # Makes the 'src' directory a Python package.
│   ├── pipeline/                   # Holds the core logic that orchestrates the multi-agent system.
│   │   └── main_pipeline.py        # The main script that runs the full agent pipeline.
│   ├── utils/                      # A collection of shared helper functions.
│   │   ├── config.py               # Handles project configuration, settings, and API keys.
│   │   └── dataset.py              # Contains functions for loading and processing the dataset.
│   └── app/                        # The web application for the user interface.
│       ├── __init__.py             # Makes 'app' a Python package.
│       ├── api.py                  # Defines the API endpoints for the web application.
│       └── web.py                  # Contains the code for the web interface, handling views and logic.
└── .gitignore                      # Specifies files and folders to be ignored by Git (e.g., '.DS_Store', 'cache').
└── environment.yml                 # The Conda file defining the project's dependencies and environment.
└── LICENSE                         # The project's license file.
└── README.md                       # The main README file with project information and setup instructions.
```