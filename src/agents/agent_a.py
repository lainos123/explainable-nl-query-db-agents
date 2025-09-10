# agent_a.py
"""
Agent A: Database Selector

This agent selects the most relevant database from the Spider dataset based on a user's natural language query.
It leverages OpenAI embeddings and a FAISS vector store to perform semantic search over processed database schemas.

Usage:
    python3 -m src.agents.agent_a

Make sure you have already run:
    python3 -m scripts.process_schemas
    python3 -m scripts.create_embeddings

before using this agent, to ensure the schema embeddings are available.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import json
import pprint

# Import project config
from src.config import PROJECT_ROOT, EMBEDDINGS_FOLDER, SCHEMA_PROCESSED_FILE

# Add project root to Python path
sys.path.append(str(PROJECT_ROOT))

# Import LangChain components
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate

# --- 1.1 OpenAI Setup ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "not-set")
print("OpenAI API key used:", OPENAI_API_KEY[:5] + "****")


# Load processed schema from JSONL
def load_processed_schema(input_file):
    """Load processed schema JSONL back into a list of strings."""
    with open(input_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines


# Use it
final_schema_result = load_processed_schema(SCHEMA_PROCESSED_FILE)
print(f"Loaded {len(final_schema_result)} entries from {SCHEMA_PROCESSED_FILE}")

# Step 1: create embeddings + vectorstore
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(final_schema_result, embeddings)

# Step 2: save embeddings
vectorstore.save_local(str(EMBEDDINGS_FOLDER))
print(f"Saved schema embeddings to {EMBEDDINGS_FOLDER}")


# --- 1.2 Database Selection Agent ---
def create_database_selection_agent(top_k):
    """Create the database selection agent using a prebuilt FAISS vectorstore"""

    llm = ChatOpenAI(model="gpt-5-mini", temperature=0)

    prompt_db = PromptTemplate(
        input_variables=["query", "retrieved_schema"],
        template="""
Please select the single most relevant database and table to answer the user's query.

User query: {query}
Schema info: {retrieved_schema}

Respond **only** with a valid JSON object (no backticks, no extra text). 
The JSON must include the following keys: "db_name", "tables", "columns", and "reasons". 
Each key should appear on its own line for readability.

Example format:

{{
  "db_name": "...",
  "tables": ["..."],
  "columns": ["..."],
  "reasons": "..."
}}
""",
    )

    db_chain = prompt_db | llm

    def database_selection_agent(user_query, top_k, mode="medium"):
        # Retrieve relevant schemas
        relevant_docs = vectorstore.similarity_search_with_score(user_query, k=top_k)
        retrieved_schema = ""
        for doc, score in relevant_docs:
            retrieved_schema += f"score: {score:.4f}, content: {doc.page_content}\n"

        # Invoke LLM
        response = db_chain.invoke(
            {"query": user_query, "retrieved_schema": retrieved_schema}
        )

        # Parse JSON output safely
        llm_content = (
            response.content if hasattr(response, "content") else str(response)
        )
        try:
            parsed = json.loads(llm_content)
        except json.JSONDecodeError:
            parsed = {}

        # Transform retrieved_schema string into structured list
        structured_schema = []
        for doc, score in relevant_docs:
            try:
                schema_json = json.loads(doc.page_content)
                structured_schema.append(
                    {
                        "score": round(score, 4),
                        "database": schema_json.get("database"),
                        "table": schema_json.get("table"),
                        "columns": schema_json.get("columns", []),
                    }
                )
            except json.JSONDecodeError:
                structured_schema.append(
                    {"score": round(score, 4), "raw_content": doc.page_content}
                )

        # Return based on mode
        if mode == "light":
            return parsed.get("db_name")
        elif mode == "medium":
            return {
                "retrieved_schema": structured_schema,
                "db_name": parsed.get("db_name"),
                "tables": parsed.get("tables", []),
                "columns": parsed.get("columns", []),
                "reasons": parsed.get("reasons", ""),
            }
        else:  # heavy
            return {
                "db_name": parsed.get("db_name"),
                "retrieved_schema": structured_schema,
                "tables": parsed.get("tables", []),
                "columns": parsed.get("columns", []),
                "reasons": parsed.get("reasons", ""),
                "llm_raw": response,
            }

    return database_selection_agent, vectorstore


test_queries = [
    "Find the name of all students who were in the tryout sorted in alphabetic order",
    "Find the average price of all product clothes.",
    "Show the names of artworks in ascending order of the year they are nominated in.",
    "What is the name of the department with the student that has the lowest GPA?",
    "What are the names and years of the movies that has the top 3 highest rating star?",
    "How many students does each advisor have?",
    "Count flights departing from Dallas in 2017",
    "What are the distinct creation years of the departments managed by a secretary born in state 'Alabama'?",
    "List courses worth more than 3 credits and their departments",
    "For each customer, compute total order value and sort desc.",
    "select all the deaths caused by ship",
    "Show me information about singers and their concerts",
    "I want to see student enrollment data",
    "Find information about car manufacturers and models",
    "What data do you have about movies and actors?",
    "Show me employee salary information",
    "Which produce has the most complaints where the status are still open",
]


# --- 1.3 Test Function ---
def apply_database_selector(query, mode="medium"):
    """
    Apply the database selection agent to one or more queries.

    Parameters:
        query_numbers (list or int, optional):
            - int: apply to that single test query (1-based index)
            - list of ints: apply to multiple test queries
            - None: apply to all test queries
        mode (str): "light", "medium", or "heavy" for the agent output
    """
    # Create the agent
    db_agent, vectorstore = create_database_selection_agent(top_k=5)

    print("=" * 60)
    print("APPLYING DATABASE SELECTION AGENT")
    print("=" * 60)

    # Call the agent with the selected mode
    result = db_agent(user_query=query, top_k=5, mode=mode)

    print("Agent A Selection:")
    pprint.pprint(result)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run a single test
    apply_database_selector(query=test_queries[2], mode="light")
