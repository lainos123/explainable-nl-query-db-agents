#!/usr/bin/env python3
"""
Agent C: SQL Generator

Generates SQL from a user query, database name, and recommended tables (from Agents A & B).

USAGE:
    # Test mode - interactive selection
    python3 -m src.agents.agent_c --test

    # Test mode - specific index (0-based)
    python3 -m src.agents.agent_c --test --index 1

    # Test mode with specific output mode
    python3 -m src.agents.agent_c --test --index 1 --mode medium

    # Production mode with resasoning - provide query, database, and tables directly
    python3 -m src.agents.agent_c --query "How many students?" --database "college_2" --tables '{"Tables": ["student"], "Columns": ["id", "name"]}' --mode light

    # Quiet mode (no debug output)
    python3 -m src.agents.agent_c --query "How many students?" --database "college_2" --tables '{"Tables": ["student"], "Columns": ["id", "name"]}' --mode light --quiet

    # Production mode with resasoning - provide query, database, and tables directly
    python3 -m src.agents.agent_c --query "How many students?" --database "college_2" --tables '{"Tables": ["student"], "Columns": ["id", "name"]}' --mode medium

    # Quiet mode (no debug output)
    python3 -m src.agents.agent_c --query "How many students?" --database "college_2" --tables '{"Tables": ["student"], "Columns": ["id", "name"]}' --quiet

PARAMETERS:
    --test                    Run in test mode (interactive or with --index)
    --index INDEX            Test case index (0-based) when using --test
    --query QUERY            User's natural language question
    --database DATABASE      Database name (from Agent A)
    --tables TABLES          Tables in JSON format from Agent B or comma-separated list
    --mode {light,medium,heavy}  Output mode (default: light)
    --quiet                  Quiet mode - only returns SQL query (no debug output)

MODES:
    - "light": SQL string only (no debug output)
    - "medium": Includes query, database, tables, SQL + prints model inputs/outputs
    - "heavy": Adds full schema and raw LLM response + prints model inputs/outputs

Debug Output (medium/heavy modes):
    - Model Inputs: user query, database name, recommended tables, full schema JSON
    - Model Outputs: raw LLM response, cleaned SQL

Depends on AI-friendly combined schema, test data, OpenAI API, and LangChain.

Example output:
{
    "User Query": "How many students are enrolled?",
    "Database Name": "college_2",
    "Recommended Tables": ["student", "enrollment"],
    "SQL": "SELECT COUNT(*) FROM student s JOIN enrollment e ON s.id = e.student_id"
}
"""

import json
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Union, Optional

# Import project config
from src.config import PROJECT_ROOT, PROCESSED_SCHEMA_AI_FRIENDLY, SQL_TESTING_PATH

# Add project root to Python path
sys.path.append(str(PROJECT_ROOT))

# Import LangChain components
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Global quiet mode flag
QUIET_MODE = False


# --- 1.1 Setup ---
def setup_llm():
    """Initialize and return the LLM for SQL generation"""
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        return llm
    except Exception as e:
        if not QUIET_MODE:
            print(f"Error setting up LLM: {e}")
        return None


# --- 1.2 Utility Functions ---
def get_true_query_toks(
    db_id: str, question: str, data_file: Path = SQL_TESTING_PATH
) -> Optional[List[str]]:
    """
    Retrieve the 'query_toks' for a given db_id and question from the test data file.

    This function helps test and debug the mapping between questions and their ground truth SQL tokens
    in the Spider test data (see data/test/spider_query_answers.json).

    Args:
        db_id (str): The database ID to match
        question (str): The question string to match
        data_file (Path): Path to the JSON test data file

    Returns:
        Optional[List[str]]: The list of SQL tokens if found, else None
    """
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Print all questions for the db_id to help debug
        if not QUIET_MODE:
            print(f"Testing: All questions for db_id={db_id}:")
        found = False
        for item in data:
            if item.get("db_id") == db_id:
                if item.get("question") == question:
                    found = True
                    if not QUIET_MODE:
                        print("  --> Matched question!")
                        print(f"  guery_toks: {item.get('guery_toks')}")
                    return item.get(
                        "guery_toks"
                    )  # Note: keeping original typo from data

        if not found and not QUIET_MODE:
            print(f"Question not found for db_id={db_id}: '{question}'")
        return None
    except Exception as e:
        if not QUIET_MODE:
            print(f"Error loading test data: {e}")
        return None


def tokenize_sql(sql: str) -> List[str]:
    """Simple SQL tokenizer: split on whitespace and punctuation"""
    return [tok for tok in re.split(r"(\W)", sql) if tok.strip()]


def compare_sql_to_ground_truth(
    sql_query: str, db_id: str, question: str, data_file: Path = SQL_TESTING_PATH
) -> bool:
    """
    Tokenizes the given SQL query and compares its tokens to the ground truth tokens
    for the specified db_id and question.

    Args:
        sql_query (str): The SQL query to compare
        db_id (str): The database ID
        question (str): The natural language question
        data_file (Path): Path to the JSON test data file

    Returns:
        bool: True if the tokenized SQL matches the ground truth tokens, False otherwise
    """
    gt_tokens = get_true_query_toks(db_id, question, data_file)
    if gt_tokens is None:
        if not QUIET_MODE:
            print(f"No ground truth found for db_id={db_id}, question={question}")
        return False

    sql_tokens = tokenize_sql(sql_query)
    return sql_tokens == gt_tokens


def clean_sql(sql_string: str) -> str:
    """Clean SQL string by removing code fences and unnecessary formatting"""
    sql_string = sql_string.strip()

    # Remove code fences if present
    if sql_string.startswith("```") and sql_string.endswith("```"):
        lines = sql_string.splitlines()
        if len(lines) > 2:
            sql_string = "\n".join(lines[1:-1])  # remove ```sql and ```

    # Remove surrounding parentheses if it's a tuple string
    if sql_string.startswith("(") and sql_string.endswith(")"):
        sql_string = sql_string[1:-1].strip().strip("'").strip('"')

    return sql_string


# --- 1.3 Prompt Template ---
generate_sql_prompt = PromptTemplate(
    input_variables=["user_query", "db_schema_json", "recommended_tables"],
    template="""
You are an SQL expert. Given the following database schema:

DB schema JSON: {db_schema_json}

You are also provided with a list of recommended tables from the schema that are likely to be relevant for answering the question.

Recommended tables: {recommended_tables}

Write a SQL query that answers the following question:

User query: {user_query}

Only return the SQL query, nothing else.

Make sure your SQL is formatted so that it is easily tokenizable: 
- Use clear spacing around punctuation (e.g., SELECT name , age FROM table WHERE id = 5)
- Avoid unnecessary line breaks or indentation
- Do not include comments or explanations
- Use proper SQL syntax and table/column names from the schema
- Be case insensitive as the schema data may have mixed case
""",
)


# --- 1.4 Main Agent Function ---
def agent_c(
    user_query: str, db_name: str, recommended_tables: List[str], mode: str = "medium"
) -> Union[str, Dict[str, Any]]:
    """
    Generate SQL query from user query, database name, and recommended tables.

    Args:
        user_query (str): The natural language question to answer
        db_name (str): Name of the database (from Agent A)
        recommended_tables (List[str]): List of recommended tables (from Agent B)
        mode (str): Output mode - "light", "medium", or "heavy"

    Returns:
        Union[str, Dict[str, Any]]: SQL query string (light mode) or structured results

    Raises:
        ValueError: If mode is not one of the supported options
        FileNotFoundError: If AI-friendly schema file doesn't exist
    """

    # Setup LLM
    llm = setup_llm()
    if llm is None:
        return {"error": "Failed to setup LLM"}

    # Create chain
    db_chain = generate_sql_prompt | llm

    try:
        # Load AI-friendly combined schema
        if not PROCESSED_SCHEMA_AI_FRIENDLY.exists():
            raise FileNotFoundError(
                f"AI-friendly schema file not found: {PROCESSED_SCHEMA_AI_FRIENDLY}"
            )

        with open(PROCESSED_SCHEMA_AI_FRIENDLY, "r", encoding="utf-8") as f:
            combined_schema = json.load(f)

        # Get the specific database schema using Franco's structure
        if db_name not in combined_schema.get("schema", {}):
            return {"error": f"Database '{db_name}' not found in schema"}

        db_schema = combined_schema["schema"][db_name]
        full_schema = db_schema.get("tables", {})

        if not full_schema:
            return {"error": f"No tables found for database: {db_name}"}

        # Debug printing for model inputs (medium and heavy modes, not in quiet mode)
        if mode in ["medium", "heavy"] and not QUIET_MODE:
            print("\n" + "=" * 60)
            print("MODEL INPUTS ")
            print("=" * 60)
            print(f"User Query: {user_query}")
            print(f"Database Name: {db_name}")
            print(f"Recommended Tables: {recommended_tables}")
            print(f"Available Tables: {list(full_schema.keys())}")
            print("\nFull Schema JSON:")
            print(json.dumps(full_schema, indent=2, ensure_ascii=False))
            print("=" * 60)

        # Run LLM
        response = db_chain.invoke(
            {
                "user_query": user_query,
                "db_schema_json": full_schema,
                "recommended_tables": recommended_tables,
            }
        )

        # Safely parse LLM output
        llm_selection_content = (
            response.content if hasattr(response, "content") else str(response)
        )

        # Try to parse as JSON first, fallback to direct content
        try:
            parsed = json.loads(llm_selection_content)
            sql = parsed.get("sql", llm_selection_content)
        except json.JSONDecodeError:
            sql = llm_selection_content.strip()

        # Clean SQL
        sql = clean_sql(sql)

        # Debug printing for model outputs (medium and heavy modes, not in quiet mode)
        if mode in ["medium", "heavy"] and not QUIET_MODE:
            print("\n" + "=" * 60)
            print("MODEL OUTPUTS ")
            print("=" * 60)
            print("Raw LLM Response:")
            print(llm_selection_content)
            print(f"\nCleaned SQL: {sql}")
            print("=" * 60)

        # Return based on mode
        if mode == "light" or QUIET_MODE:
            return sql  # just the SQL string

        elif mode == "medium":
            return {
                "User Query": user_query,
                "Database Name": db_name,
                "Recommended Tables": recommended_tables,
                "SQL": sql,
            }

        elif mode == "heavy":
            return {
                "User Query": user_query,
                "Database Name": db_name,
                "Recommended Tables": recommended_tables,
                "SQL": sql,
                "Full Schema": full_schema,
                "Raw LLM Response": response,
            }

        else:
            raise ValueError(
                f"Unknown mode: {mode}. Must be 'light', 'medium', or 'heavy'"
            )

    except Exception as e:
        return {"error": f"Error in agent_c: {str(e)}"}


# --- 1.5 Test Function ---
def test_agent_c():
    """Test Agent C with sample queries"""
    if not QUIET_MODE:
        print("=" * 60)
        print("TESTING AGENT C: SQL GENERATOR")
        print("=" * 60)

    # Test cases with different databases and tables (using JSON structure format)
    test_cases = [
        {
            "query": "How many heads of the departments are older than 56 ?",
            "db_name": "department_management",
            "tables": ["department", "head"],
        },
        {
            "query": "What are the distinct buildings with capacities of greater than 50?",
            "db_name": "college_2",
            "tables": ["student", "course", "takes"],
        },
        {
            "query": "What is the name of the song that was released in the most recent year?",
            "db_name": "music_1",
            "tables": ["singer", "concert"],
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        if not QUIET_MODE:
            print(f"\nTest {i}: {test_case['query']}")
            print(f"Database: {test_case['db_name']}")
            print(f"Tables: {test_case['tables']}")
            print(f"Mode: {test_case['mode']}")
            print("-" * 50)

        result = agent_c(
            test_case["query"],
            test_case["db_name"],
            test_case["tables"],
            test_case["mode"],
        )

        if "error" in result:
            if not QUIET_MODE:
                print(f"Error: {result['error']}")
        else:
            if test_case["mode"] == "light" or QUIET_MODE:
                if not QUIET_MODE:
                    print(f"Generated SQL: {result}")
                else:
                    print(result)
            else:
                if not QUIET_MODE:
                    # Pretty print the result
                    for key, value in result.items():
                        if isinstance(value, (dict, list)):
                            pretty_value = json.dumps(
                                value, indent=2, ensure_ascii=False
                            )
                            print(f"{key}: {pretty_value}")
                        else:
                            print(f"{key}: {value}")
                else:
                    print(result)

        # Test ground truth comparison if test data is available
        if SQL_TESTING_PATH.exists() and not QUIET_MODE:
            print("\nTesting against ground truth...")
            is_correct = compare_sql_to_ground_truth(
                result if isinstance(result, str) else result.get("SQL", ""),
                test_case["db_name"],
                test_case["query"],
            )
            print(f"Matches ground truth: {is_correct}")

        if not QUIET_MODE:
            print("\n" + "=" * 60)


# --- 1.6 Command Line Interface ---
def main():
    """Main function for command line interface"""
    global QUIET_MODE

    parser = argparse.ArgumentParser(description="Agent C: SQL Generator")

    # Test mode arguments
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    parser.add_argument("--index", type=int, help="Test case index (0-based)")

    # Production mode arguments
    parser.add_argument("--query", type=str, help="User query")
    parser.add_argument("--database", type=str, help="Database name")
    parser.add_argument(
        "--tables",
        type=str,
        help='Comma-separated list of tables OR JSON string from Agent B (e.g., \'{"Tables": ["student"], "Columns": ["id", "name"]}\')',
    )

    # General arguments
    parser.add_argument(
        "--mode",
        type=str,
        default="light",
        choices=["light", "medium", "heavy"],
        help="Output mode",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Quiet mode (no debug output)"
    )

    args = parser.parse_args()

    # Set quiet mode
    QUIET_MODE = args.quiet

    # Check if AI-friendly schema exists
    if not PROCESSED_SCHEMA_AI_FRIENDLY.exists():
        print("Error: AI-friendly schema file not found!")
        print("Please run: python3 scripts/Schema_Generation.py")
        sys.exit(1)

    # Check if test data exists
    if not SQL_TESTING_PATH.exists():
        if not QUIET_MODE:
            print("Warning: Test data file not found!")
            print("Please run: python3 -m scripts.load_test_data")
            print("Continuing without ground truth comparison...")

    if args.test:
        # Test mode
        if args.index is not None:
            # Run specific test case
            test_cases = [
                {
                    "query": "How many heads of the departments are older than 56 ?",
                    "db_name": "department_management",
                    "tables": ["department", "head"],
                    "mode": args.mode,
                },
                {
                    "query": "What are the distinct buildings with capacities of greater than 50?",
                    "db_name": "college_2",
                    "tables": ["student", "course", "takes"],
                    "mode": args.mode,
                },
                {
                    "query": "What is the name of the song that was released in the most recent year?",
                    "db_name": "music_1",
                    "tables": ["singer", "concert"],
                    "mode": args.mode,
                },
            ]

            if 0 <= args.index < len(test_cases):
                test_case = test_cases[args.index]
                result = agent_c(
                    test_case["query"],
                    test_case["db_name"],
                    test_case["tables"],
                    test_case["mode"],
                )
                print(result)
            else:
                print(
                    f"Error: Test index {args.index} out of range. Available: 0-{len(test_cases) - 1}"
                )
                sys.exit(1)
        else:
            # Run all test cases
            test_agent_c()
    else:
        # Production mode
        if not args.query or not args.database or not args.tables:
            print("Error: Production mode requires --query, --database, and --tables")
            print("Use --test for test mode or provide all required arguments")
            sys.exit(1)

        # Parse tables - handle both JSON from Agent B and comma-separated lists
        try:
            # Try to parse as JSON first (from Agent B output)
            tables_data = json.loads(args.tables)
            if isinstance(tables_data, dict) and "Tables" in tables_data:
                tables = tables_data["Tables"]
                if not QUIET_MODE:
                    print(
                        f"Parsed Agent B output: Tables={tables}, Columns={tables_data.get('Columns', [])}"
                    )
            else:
                tables = tables_data if isinstance(tables_data, list) else [tables_data]
        except json.JSONDecodeError:
            # Fallback to comma-separated string
            tables = [t.strip() for t in args.tables.split(",")]

        # Run agent
        result = agent_c(args.query, args.database, tables, args.mode)
        print(result)


# --- 1.7 Main Execution ---
if __name__ == "__main__":
    main()
