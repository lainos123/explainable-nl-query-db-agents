import json
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from utils.schema_builder import get_schema_dir


def create_chain(api_key: str):
    llm = ChatOpenAI(model="gpt-5-mini", temperature=0, api_key=api_key)

    list_tables_prompt = PromptTemplate(
        input_variables=["user_query", "db_schema_json"],
        template=(
            "Given the selected database schema, return ONLY valid JSON with exactly these keys\n"
            '  "relevant_tables": ["..."],\n'
            '  "reasons": "..." \n\n'
            "User query: {user_query}\n"
            "DB schema JSON: {db_schema_json}\n"
            "Do not wrap all_tables in an extra list. Do not include any text outside JSON."
        ),
    )
    return list_tables_prompt | llm


def run(api_key, payload: dict, user_id: int):
    """
    Agent B entrypoint.
    Now accepts only the database name in the payload and will read the per-user schema file
    to build the `db_schema_json` passed to the LLM.

    Expected payload (from Agent A via views):
    {
        "query": "...",
        "database": "...",
        "reasons": "..."
    }
    """
    try:
        user_query = payload.get("query")
        db_name = payload.get("database")

        if not user_query:
            return {"error": "query is required"}
        if not db_name:
            return {"error": "database is required"}

        # Load schema_ab.jsonl for this user and pick entries for the selected database
        schema_dir = get_schema_dir(user_id)
        schema_file = os.path.join(schema_dir, "schema_ab.jsonl")
        tables = []
        columns = []
        db_schema = {"tables": [], "columns": []}

        if os.path.exists(schema_file):
            with open(schema_file, "r", encoding="utf-8") as sf:
                for line in sf:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    if obj.get("database") == db_name:
                        tables.append(obj.get("table"))
                        cols = obj.get("columns", []) or []
                        for c in cols:
                            if c not in columns:
                                columns.append(c)

        db_schema["tables"] = tables
        db_schema["columns"] = columns

        chain = create_chain(api_key)
        response = chain.invoke({
            "user_query": user_query,
            "db_schema_json": json.dumps(db_schema, ensure_ascii=False),
        })
        raw = response.content if hasattr(response, "content") else str(response)

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"error": "invalid LLM output", "raw": raw}

        # Return minimal fields: query, database, table(s), reasons
        relevant_tables = parsed.get("relevant_tables", []) if isinstance(parsed, dict) else []
        reasons = parsed.get("reasons", "") if isinstance(parsed, dict) else ""

        # Provide both keys for compatibility: `tables` (frontend/rendering) and `relevant_tables` (agent C)
        return {
            "query": user_query,
            "database": db_name,
            "tables": relevant_tables,
            "relevant_tables": relevant_tables,
            "reasons": reasons,
        }

    except Exception as e:
        return {"error": f"Agent B failed: {str(e)}"}