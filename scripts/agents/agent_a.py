# agent_a.py
"""
Agent A: Database Selector

This agent selects the most relevant database from the Spider dataset based on a user's natural language query.
It leverages OpenAI embeddings and a FAISS vector store to perform semantic search over processed database schemas.

Usage:
    # Test mode - interactive selection
    python3 -m scripts.agents.agent_a --test

    # Test mode - specific index (0-based)
    python3 -m scripts.agents.agent_a --test --index 5

    # Test mode with specific output mode and top_k
    python3 -m scripts.agents.agent_a --test --index 5 --mode medium --top_k 10

    # Production mode - provide query directly
    python3 -m scripts.agents.agent_a --query "your query here"

    # Production mode with specific output mode and top_k
    python3 -m scripts.agents.agent_a --query "your query here" --mode heavy --top_k 3

    # Quiet mode for multi-agent systems (suppresses all print statements)
    python3 -m scripts.agents.agent_a --query "your query here" --quiet

Parameters:
    --test: Run in test mode (interactive or with --index)
    --index: Test query index (0-based, only with --test)
    --query: Custom query to process (production mode)
    --mode: Output mode - "light" (default), "medium", or "heavy"
    --top_k: Number of similar schemas to retrieve (default: 5)
    --quiet: Suppress all print statements (useful for multi-agent systems)

Make sure you have already run:
    python3 -m scripts.process_schemas
    python3 -m scripts.create_embeddings

before using this agent, to ensure the schema embeddings are available.
"""

import argparse
import json
import os
import pprint
import sys

# Import project config
from scripts.config import EMBEDDINGS_FOLDER, PROJECT_ROOT, SCHEMA_PROCESSED_FILE

# Add project root to Python path
sys.path.append(str(PROJECT_ROOT))

# Import LangChain components
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Global variable for quiet mode
QUIET_MODE = False

# --- 1.1 OpenAI Setup ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "not-set")


# Load processed schema from JSONL
def load_processed_schema(input_file):
    """Load processed schema JSONL back into a list of strings."""
    with open(input_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines


def check_embeddings_exist():
    """Check if embeddings already exist."""
    return EMBEDDINGS_FOLDER.exists() and any(EMBEDDINGS_FOLDER.iterdir())


def create_or_load_embeddings():
    """Create embeddings only if they don't already exist, otherwise load them."""
    if check_embeddings_exist():
        if not QUIET_MODE:
            print(f"Embeddings already exist at {EMBEDDINGS_FOLDER}, loading...")
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.load_local(
            str(EMBEDDINGS_FOLDER), embeddings, allow_dangerous_deserialization=True
        )
        if not QUIET_MODE:
            print(f"Loaded existing embeddings from {EMBEDDINGS_FOLDER}")
        return vectorstore
    else:
        if not QUIET_MODE:
            print(f"Embeddings not found at {EMBEDDINGS_FOLDER}, creating new ones...")
        final_schema_result = load_processed_schema(SCHEMA_PROCESSED_FILE)
        if not QUIET_MODE:
            print(
                f"Loaded {len(final_schema_result)} entries from {SCHEMA_PROCESSED_FILE}"
            )

        # Step 1: create embeddings + vectorstore
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_texts(final_schema_result, embeddings)

        # Step 2: save embeddings
        vectorstore.save_local(str(EMBEDDINGS_FOLDER))
        if not QUIET_MODE:
            print(f"Saved schema embeddings to {EMBEDDINGS_FOLDER}")
        return vectorstore


# --- 1.2 Database Selection Agent ---
def create_database_selection_agent(top_k, vectorstore):
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
                        "score": round(float(score), 4),  # Convert to regular float
                        "database": schema_json.get("database"),
                        "table": schema_json.get("table"),
                        "columns": schema_json.get("columns", []),
                    }
                )
            except json.JSONDecodeError:
                structured_schema.append(
                    {
                        "score": round(float(score), 4),
                        "raw_content": doc.page_content,
                    }  # Convert to regular float
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
            result = {
                "db_name": parsed.get("db_name"),
                "retrieved_schema": structured_schema,
                "tables": parsed.get("tables", []),
                "columns": parsed.get("columns", []),
                "reasons": parsed.get("reasons", ""),
            }

            # Only include raw LLM response if not in quiet mode
            if not QUIET_MODE:
                result["llm_raw"] = response

            return result

    return database_selection_agent


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


def display_test_queries():
    """Display available test queries with their indices."""
    if QUIET_MODE:
        return
    print("\nAvailable test queries:")
    print("=" * 60)
    for i, query in enumerate(test_queries):
        print(f"{i:2d}: {query}")
    print("=" * 60)


def get_test_query_index():
    """Get test query index from user input."""
    while True:
        try:
            index = input(
                f"\nEnter test query index (0-{len(test_queries) - 1}): "
            ).strip()
            if not index:
                return 0  # Default to first query
            index = int(index)
            if 0 <= index < len(test_queries):
                return index
            else:
                print(f"Please enter a number between 0 and {len(test_queries) - 1}")
        except ValueError:
            print("Please enter a valid number")


# --- 1.3 Test Function ---
def apply_database_selector(query, mode="light", top_k=5):
    """
    Apply the database selection agent to a query.

    Parameters:
        query (str): The query to process
        mode (str): "light", "medium", or "heavy" for the agent output
        top_k (int): Number of similar schemas to retrieve
    """
    # Load or create embeddings
    vectorstore = create_or_load_embeddings()

    # Create the agent
    db_agent = create_database_selection_agent(top_k=top_k, vectorstore=vectorstore)

    if not QUIET_MODE:
        print("=" * 60)
        print("APPLYING DATABASE SELECTION AGENT")
        print("=" * 60)

    # Get similarity search results first
    relevant_docs = vectorstore.similarity_search_with_score(query, k=top_k)

    # Print similarity search results for medium and heavy modes
    if mode in ["medium", "heavy"] and not QUIET_MODE:
        print("\n" + "=" * 60)
        print("SIMILARITY SEARCH RESULTS")
        print("=" * 60)
        print(f"Retrieved {len(relevant_docs)} similar schemas:")
        for i, (doc, score) in enumerate(relevant_docs, 1):
            print(f"\n{i}. Score: {score:.4f}")
            try:
                schema_json = json.loads(doc.page_content)
                print(f"   Database: {schema_json.get('database', 'N/A')}")
                print(f"   Table: {schema_json.get('table', 'N/A')}")
                print(f"   Columns: {schema_json.get('columns', [])}")
            except json.JSONDecodeError:
                print(f"   Raw content: {doc.page_content}")

    # Call the agent with the selected mode
    result = db_agent(user_query=query, top_k=top_k, mode=mode)

    if not QUIET_MODE:
        print("\n" + "=" * 60)
        print("AGENT A SELECTION")
        print("=" * 60)
        pprint.pprint(result)
        print("\n" + "=" * 60)

    return result


def main():
    """Main function to handle command line arguments and execute the agent."""
    global QUIET_MODE

    parser = argparse.ArgumentParser(description="Agent A: Database Selector")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    parser.add_argument("--index", type=int, help="Test query index (0-based)")
    parser.add_argument("--query", type=str, help="Custom query to process")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["light", "medium", "heavy"],
        default="light",
        help="Output mode (default: light)",
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=5,
        help="Number of similar schemas to retrieve (default: 5)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress all print statements (useful for multi-agent systems)",
    )

    args = parser.parse_args()
    QUIET_MODE = args.quiet

    # Print API key info after setting QUIET_MODE
    if not QUIET_MODE:
        print("OpenAI API key used:", OPENAI_API_KEY[:5] + "****")

    if args.test:
        # Test mode
        if args.index is not None:
            # Specific index provided
            if 0 <= args.index < len(test_queries):
                query = test_queries[args.index]
                if not QUIET_MODE:
                    print(f"Running test query {args.index}: {query}")
                result = apply_database_selector(
                    query, mode=args.mode, top_k=args.top_k
                )
                if QUIET_MODE:
                    print(json.dumps(result, indent=2))
            else:
                if not QUIET_MODE:
                    print(
                        f"Error: Index {args.index} is out of range (0-{len(test_queries) - 1})"
                    )
                sys.exit(1)
        else:
            # Interactive selection
            display_test_queries()
            index = get_test_query_index()
            query = test_queries[index]
            if not QUIET_MODE:
                print(f"\nRunning test query {index}: {query}")
            result = apply_database_selector(query, mode=args.mode, top_k=args.top_k)
            if QUIET_MODE:
                print(json.dumps(result, indent=2))

    elif args.query:
        # Production mode with custom query
        if not QUIET_MODE:
            print(f"Processing custom query: {args.query}")
        result = apply_database_selector(args.query, mode=args.mode, top_k=args.top_k)
        if QUIET_MODE:
            print(json.dumps(result, indent=2))

    else:
        # No arguments provided - show help
        parser.print_help()
        print("\nExamples:")
        print("  python3 -m scripts.agents.agent_a --test")
        print("  python3 -m scripts.agents.agent_a --test --index 5")
        print(
            "  python3 -m scripts.agents.agent_a --test --index 5 --mode medium --top_k 10"
        )
        print("  python3 -m scripts.agents.agent_a --query 'Find all students'")
        print(
            "  python3 -m scripts.agents.agent_a --query 'Find all students' --mode medium --top_k 3"
        )
        print("  python3 -m scripts.agents.agent_a --query 'Find all students' --quiet")


if __name__ == "__main__":
    main()
