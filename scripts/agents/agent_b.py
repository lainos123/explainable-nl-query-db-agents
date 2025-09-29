#!/usr/bin/env python3
"""
Agent B: Table and Column Selector

Selects relevant tables and columns from a database based on a user query.
Used after Agent A picks the database.

USAGE:
    # Test mode - interactive selection
    python3 -m scripts.agents.agent_b --test

    # Test mode - specific index (0-based)
    python3 -m scripts.agents.agent_b --test --index 1

    # Test mode with specific output mode
    python3 -m scripts.agents.agent_b --test --index 1 --mode medium

    # Production mode - provide query and database directly
    python3 -m scripts.agents.agent_b --query "How many students are enrolled?" --database "college_2"

    # Production mode with specific output mode
    python3 -m scripts.agents.agent_b --query "How many students are enrolled?" --database "college_2" --mode heavy

    # Quiet mode for multi-agent systems (suppresses all print statements)
    python3 -m scripts.agents.agent_b --query "How many students?" --database "college_2" --quiet

Parameters:
    --test: Run in test mode (interactive or with --index)
    --index: Test query index (0-based, only with --test)
    --query: Custom query to process (production mode)
    --database: Database name to use (production mode)
    --mode: Output mode - "light" (default), "medium", or "heavy"
    --quiet: Suppress all print statements (useful for multi-agent systems)

MODES:
    - "light": Only tables and columns
    - "medium": Includes query, database, tables, columns, reasons
    - "heavy": Adds full schema and raw LLM response

Depends on processed schemas and OpenAI API.

Example output:
{
    "User Query": "How many students are enrolled?",
    "Database Name": "college_2",
    "Tables": ["student", "enrollment"],
    "Columns": ["student_id", "name", "enrollment_date"],
    "Reasons": "Student table contains enrollment data..."
}
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Union

# Import project config
from scripts.config import PROJECT_ROOT, SCHEMA_PROCESSED_FILE

# Add project root to Python path
sys.path.append(str(PROJECT_ROOT))

# Import LangChain components
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate


# --- 1.1 Setup ---
def setup_llm():
    """Initialize and return the LLM for table/column selection"""
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        return llm
    except Exception as e:
        if not QUIET_MODE:
            print(f"Error setting up LLM: {e}")
        return None


# --- 1.2 Prompt Template ---
list_tables_prompt = PromptTemplate(
    input_variables=["user_query", "db_schema_json"],
    template="""
Given the relevant database schema, return the tables and columns that are most relevant to the user's query.

User query: {user_query}
DB schema JSON: {db_schema_json}

Respond ONLY with a valid JSON object (no extra text, no backticks). 
The JSON must include the following keys: "relevant_tables", "relevant_columns", and "reasons". 

Example format (output must match this structure exactly): 

{{
  "relevant_tables": ["table1", "table2"],
  "relevant_columns": ["column1", "column2", "column3"],
  "reasons": "Explanation of why these tables and columns are relevant to the query"
}}

Do not include any text outside the JSON object.
""",
)


# --- 1.3 Main Agent Function ---
def agent_b(user_query: str, db_name: str, mode: str = "light") -> Dict[str, Any]:
    """
    Select relevant tables and columns from a database schema based on a user query.

    Args:
        user_query (str): The natural language question to answer
        db_name (str): Name of the database (selected by Agent A)
        mode (str): Output mode - "light", "medium", or "heavy"

    Returns:
        Dict[str, Any]: Structured selection results based on mode

    Raises:
        ValueError: If mode is not one of the supported options
        FileNotFoundError: If processed schema file doesn't exist
        json.JSONDecodeError: If LLM response is not valid JSON
    """

    # Setup LLM
    llm = setup_llm()
    if llm is None:
        return {"error": "Failed to setup LLM"}

    # Create chain
    db_chain = list_tables_prompt | llm

    try:
        # Load schema lines
        if not SCHEMA_PROCESSED_FILE.exists():
            raise FileNotFoundError(
                f"Processed schema file not found: {SCHEMA_PROCESSED_FILE}"
            )

        with open(SCHEMA_PROCESSED_FILE, "r", encoding="utf-8") as f:
            schema_lines = f.readlines()

        # Parse JSON lines and filter for the selected database
        full_schema = []
        for line in schema_lines:
            try:
                parsed_line = json.loads(line.strip())
                if parsed_line.get("database") == db_name:
                    full_schema.append(parsed_line)
            except json.JSONDecodeError:
                continue  # Skip invalid JSON lines

        if not full_schema:
            return {"error": f"No schema found for database: {db_name}"}

        # Run LLM
        response = db_chain.invoke(
            {"user_query": user_query, "db_schema_json": full_schema}
        )

        # Parse LLM output into dict
        llm_selection_content = (
            response.content if hasattr(response, "content") else str(response)
        )

        try:
            parsed = json.loads(llm_selection_content)
        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse LLM response as JSON: {e}",
                "raw_response": llm_selection_content,
            }

        # Return based on mode
        if mode == "light":
            return {
                "Tables": parsed.get("relevant_tables", []),
                "Columns": parsed.get("relevant_columns", []),
            }

        elif mode == "medium":
            return {
                "User Query": user_query,
                "Database Name": db_name,
                "Tables": parsed.get("relevant_tables", []),
                "Columns": parsed.get("relevant_columns", []),
                "Reasons": parsed.get("reasons", ""),
            }

        elif mode == "heavy":
            result = {
                "User Query": user_query,
                "Database Name": db_name,
                "Full Schema": full_schema,
                "Tables": parsed.get("relevant_tables", []),
                "Columns": parsed.get("relevant_columns", []),
                "Reasons": parsed.get("reasons", ""),
            }

            # Only include raw LLM response if not in quiet mode
            if not QUIET_MODE:
                result["Raw LLM Response"] = response

            return result

        else:
            raise ValueError(
                f"Unknown mode: {mode}. Must be 'light', 'medium', or 'heavy'"
            )

    except Exception as e:
        return {"error": f"Error in agent_b: {str(e)}"}


# --- 1.4 Test Cases ---
test_cases = [
    {
        "query": "How many heads of the departments are older than 56?",
        "db_name": "department_management",
    },
    {
        "query": "What are the names of all students enrolled in computer science?",
        "db_name": "college_2",
    },
    {
        "query": "Show me information about singers and their concerts",
        "db_name": "music_1",
    },
]


def display_test_cases():
    """Display available test cases with their indices."""
    if QUIET_MODE:
        return
    print("\nAvailable test cases:")
    print("=" * 60)
    for i, test_case in enumerate(test_cases):
        print(f"{i:2d}: Query: {test_case['query']}")
        print(f"    Database: {test_case['db_name']}")
        print()
    print("=" * 60)


def get_test_case_index():
    """Get test case index from user input."""
    while True:
        try:
            index = input(
                f"\nEnter test case index (0-{len(test_cases) - 1}): "
            ).strip()
            if not index:
                return 0  # Default to first test case
            index = int(index)
            if 0 <= index < len(test_cases):
                return index
            else:
                print(f"Please enter a number between 0 and {len(test_cases) - 1}")
        except ValueError:
            print("Please enter a valid number")


def run_test_case(test_case, mode="light"):
    """Run a single test case and display results."""
    if not QUIET_MODE:
        print(f"\nQuery: {test_case['query']}")
        print(f"Database: {test_case['db_name']}")
        print(f"Mode: {mode}")
        print("-" * 50)

    result = agent_b(test_case["query"], test_case["db_name"], mode)

    if "error" in result:
        if not QUIET_MODE:
            print(f"Error: {result['error']}")
    else:
        if not QUIET_MODE:
            # Pretty print the result, using json.dumps for complex values
            for key, value in result.items():
                if isinstance(value, (dict, list)):
                    pretty_value = json.dumps(value, indent=2, ensure_ascii=False)
                    print(f"{key}: {pretty_value}")
                else:
                    print(f"{key}: {value}")

    if not QUIET_MODE:
        print("\n" + "=" * 60)

    return result


def main():
    """Main function to handle command line arguments and execute the agent."""
    global QUIET_MODE
    QUIET_MODE = False

    parser = argparse.ArgumentParser(description="Agent B: Table and Column Selector")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    parser.add_argument("--index", type=int, help="Test case index (0-based)")
    parser.add_argument("--query", type=str, help="Custom query to process")
    parser.add_argument("--database", type=str, help="Database name to use")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["light", "medium", "heavy"],
        default="light",
        help="Output mode (default: light)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress all print statements (useful for multi-agent systems)",
    )

    args = parser.parse_args()
    QUIET_MODE = args.quiet

    # Check if processed schemas exist
    if not SCHEMA_PROCESSED_FILE.exists():
        if not QUIET_MODE:
            print("Error: Processed schema file not found!")
            print("Please run: python3 -m scripts.process_schemas")
        sys.exit(1)

    if args.test:
        # Test mode
        if args.index is not None:
            # Specific index provided
            if 0 <= args.index < len(test_cases):
                test_case = test_cases[args.index]
                if not QUIET_MODE:
                    print(f"Running test case {args.index}")
                result = run_test_case(test_case, mode=args.mode)
                if QUIET_MODE:
                    print(json.dumps(result, indent=2))
            else:
                if not QUIET_MODE:
                    print(
                        f"Error: Index {args.index} is out of range (0-{len(test_cases) - 1})"
                    )
                sys.exit(1)
        else:
            # Interactive selection
            display_test_cases()
            index = get_test_case_index()
            test_case = test_cases[index]
            if not QUIET_MODE:
                print(f"\nRunning test case {index}")
            result = run_test_case(test_case, mode=args.mode)
            if QUIET_MODE:
                print(json.dumps(result, indent=2))

    elif args.query and args.database:
        # Production mode with custom query and database
        if not QUIET_MODE:
            print(f"Processing custom query: {args.query}")
            print(f"Database: {args.database}")
            print(f"Mode: {args.mode}")
            print("-" * 50)

        result = agent_b(args.query, args.database, args.mode)

        if "error" in result:
            if not QUIET_MODE:
                print(f"Error: {result['error']}")
            else:
                print(json.dumps(result, indent=2))
        else:
            if not QUIET_MODE:
                # Pretty print the result
                for key, value in result.items():
                    if isinstance(value, (dict, list)):
                        pretty_value = json.dumps(value, indent=2, ensure_ascii=False)
                        print(f"{key}: {pretty_value}")
                    else:
                        print(f"{key}: {value}")
            else:
                # In quiet mode, output clean JSON for multi-agent systems
                print(json.dumps(result, indent=2))

    else:
        # No arguments provided - show help
        parser.print_help()
        print("\nExamples:")
        print("  python3 -m scripts.agents.agent_b --test")
        print("  python3 -m scripts.agents.agent_b --test --index 1")
        print("  python3 -m scripts.agents.agent_b --test --index 1 --mode medium")
        print(
            "  python3 -m scripts.agents.agent_b --query 'How many students?' --database 'college_2'"
        )
        print(
            "  python3 -m scripts.agents.agent_b --query 'How many students?' --database 'college_2' --mode heavy"
        )
        print(
            "  python3 -m scripts.agents.agent_b --query 'How many students?' --database 'college_2' --quiet"
        )


if __name__ == "__main__":
    main()
