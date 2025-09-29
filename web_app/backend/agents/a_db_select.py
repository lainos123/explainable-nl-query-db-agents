import json
import os
import re
from django.conf import settings
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# Helpers
def get_user_schema_dir(user_id: int) -> str:
    """Schema directory cho user trong MEDIA_ROOT/<user_id>/schema"""
    schema_dir = os.path.join(settings.MEDIA_ROOT, str(user_id), "schema")
    os.makedirs(schema_dir, exist_ok=True)
    return schema_dir


def get_user_embeddings_folder(user_id: int) -> str:
    return os.path.join(get_user_schema_dir(user_id), "embeddings")


def get_user_schema_file(user_id: int) -> str:
    return os.path.join(get_user_schema_dir(user_id), "schema_ab.jsonl")


def load_processed_schema(input_file: str):
    with open(input_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


# Embeddings + vectorstore


def create_or_load_embeddings(api_key: str, user_id: int):
    schema_file = get_user_schema_file(user_id)
    embeddings_folder = get_user_embeddings_folder(user_id)
    embeddings = OpenAIEmbeddings(api_key=api_key)

    if os.path.exists(embeddings_folder) and os.listdir(embeddings_folder):
        return FAISS.load_local(
            embeddings_folder, embeddings, allow_dangerous_deserialization=True
        )

    if not os.path.exists(schema_file):
        raise FileNotFoundError(
            f"Database file not found, please upload a database first."
        )

    schema_texts = load_processed_schema(schema_file)
    vectorstore = FAISS.from_texts(schema_texts, embeddings)
    vectorstore.save_local(embeddings_folder)
    return vectorstore


# LLM chain


def create_agent(vectorstore, api_key: str, model: str = "gpt-5-mini", top_k: int = 5):
    llm = ChatOpenAI(model=model, temperature=0, api_key=api_key)
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
  "reasons": "Explanation of why this database was selected based on the similarity scores and schema content"
}}
""",
    )

    db_chain = prompt_db | llm

    def database_selection_agent(user_query: str):
        # similarity_search_with_score returns (Document, distance). Lower distance = closer.
        relevant_docs = vectorstore.similarity_search_with_score(user_query, k=top_k)
        retrieved_schema = "\n".join(
            f"score: {score:.4f}, content: {doc.page_content}"
            for doc, score in relevant_docs
        )

        response = db_chain.invoke(
            {"query": user_query, "retrieved_schema": retrieved_schema}
        )
        raw = response.content if hasattr(response, "content") else str(response)

        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            parsed_json = (
                json.loads(match.group(0))
                if match
                else {"error": "no JSON found", "raw": raw}
            )
        except json.JSONDecodeError:
            parsed_json = {"error": "invalid LLM output", "raw": raw}

        # Transform retrieved_schema into structured list for display
        structured_schema = []
        for doc, score in relevant_docs:
            try:
                schema_json = json.loads(doc.page_content)
                distance = float(score)
                # Provide a derived similarity (1/(1+distance)); higher is better
                similarity = round(1.0 / (1.0 + max(distance, 0.0)), 6)
                structured_schema.append(
                    {
                        "similarity": similarity,
                        "database": schema_json.get("database"),
                        "table": schema_json.get("table"),
                        "columns": schema_json.get("columns", []),
                    }
                )
            except json.JSONDecodeError:
                distance = float(score)
                similarity = round(1.0 / (1.0 + max(distance, 0.0)), 6)
                structured_schema.append(
                    {
                        "similarity": similarity,
                        "raw_content": doc.page_content,
                    }
                )

        # Normalize output and include retrieved schemas
        db_name = None
        reasons = ""
        if isinstance(parsed_json, dict):
            db_name = parsed_json.get("db_name") or parsed_json.get("database")
            reasons = parsed_json.get("reasons", "")

        return {
            "query": user_query,
            "database": db_name,
            "reasons": reasons,
            "retrieved_schemas": structured_schema,
        }

    return database_selection_agent


# Entrypoint


def run(
    api_key: str, payload: dict, user_id: int, model: str = "gpt-5-mini", top_k: int = 5
):
    """
    Agent A entrypoint.

    Expected payload:
    {
        "query": "Find all students ..."
    }
    """
    try:
        user_query = payload.get("query")
        if not user_query:
            return {"error": "query is required"}

        vectorstore = create_or_load_embeddings(api_key, user_id)
        agent = create_agent(vectorstore, api_key, model=model, top_k=top_k)
        parsed = agent(user_query)

        # Return the full result including retrieved schemas
        return {
            "query": user_query,
            "database": parsed.get("database"),
            "reasons": parsed.get("reasons", ""),
            "retrieved_schemas": parsed.get("retrieved_schemas", []),
        }

    except Exception as e:
        return {"error": f"Agent A failed: {str(e)}"}
