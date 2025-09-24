import json
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from utils.schema_builder import get_schema_dir


def create_chain(api_key: str):
    llm = ChatOpenAI(model="gpt-5-mini", temperature=0, api_key=api_key)

    produce_sql_prompt = PromptTemplate(
        input_variables=["user_query", "db_schema_json", "selected_tables"],
        template=(
            "Given the selected database schema and selected table names, "
            "please be case insensitive, return ONLY valid JSON with exactly these keys\n"
            '  "relevant_tables": ["..."],\n'
            '  "SQL Code": "..."\n\n'
            '  "reasons": "..." \n\n'
            "User query: {user_query}\n"
            "DB schema JSON: {db_schema_json}\n"
            "Selected tables: {selected_tables}\n"
            "Do not wrap all_tables in an extra list. Do not include any text outside JSON."
        ),
    )
    return produce_sql_prompt | llm


def run(api_key, payload: dict, user_id: int):
    """
    Agent C entrypoint.
    Expected payload (from Agent B):
    {
        "query": "...",
        "database": "...",
        "relevant_tables": ["..."],
        "reasons": "..."
    }
    """
    try:
        user_query = payload.get("query")
        db_name = payload.get("database")
        selected_tables = payload.get("relevant_tables") or payload.get("tables") or []

        if not user_query:
            return {"error": "query is required"}
        if not db_name:
            return {"error": "database is required"}
        if not selected_tables:
            return {"error": "relevant_tables is required"}

        # Load schema_c.json for this user and pick entries for the selected database
        schema_dir = get_schema_dir(user_id)
        schema_file = os.path.join(schema_dir, "schema_c.json")

        db_schema_json = {}
        if os.path.exists(schema_file):
            with open(schema_file, "r", encoding="utf-8") as f:
                try:
                    all_schema = json.load(f)
                except Exception:
                    all_schema = {}
            db_schema_json = all_schema.get(db_name, {})
        else:
            return {"error": f"schema_c.json not found in {schema_dir}"}

        chain = create_chain(api_key)
        response = chain.invoke({
            "user_query": user_query,
            "db_schema_json": json.dumps(db_schema_json, ensure_ascii=False),
            "selected_tables": json.dumps(selected_tables, ensure_ascii=False),
        })

        raw = response.content if hasattr(response, "content") else str(response)

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"error": "invalid LLM output", "raw": raw}

        merged = {
            "query": user_query,
            "database": db_name,
            "relevant_tables": parsed.get("relevant_tables", selected_tables),
            "SQL": parsed.get("SQL") or parsed.get("SQL Code"),
            "reasons": parsed.get("reasons", payload.get("reasons", "")),
        }
        return merged

    except Exception as e:
        return {"error": f"Agent C failed: {str(e)}"}
