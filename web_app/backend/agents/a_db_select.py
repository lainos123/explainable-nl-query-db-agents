# agents/a_db_select.py
import json
import os
from django.conf import settings
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


SCHEMA_DIR = settings.SCHEMA_DIR
EMBEDDINGS_FOLDER = os.path.join(SCHEMA_DIR, "embeddings")
SCHEMA_PROCESSED_FILE = os.path.join(SCHEMA_DIR, "schema_processed.jsonl")


def load_processed_schema(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def create_or_load_embeddings():
    os.makedirs(SCHEMA_DIR, exist_ok=True)

    if os.path.exists(EMBEDDINGS_FOLDER) and os.listdir(EMBEDDINGS_FOLDER):
        embeddings = OpenAIEmbeddings()
        return FAISS.load_local(
            EMBEDDINGS_FOLDER, embeddings, allow_dangerous_deserialization=True
        )

    schema_texts = load_processed_schema(SCHEMA_PROCESSED_FILE)
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(schema_texts, embeddings)
    vectorstore.save_local(EMBEDDINGS_FOLDER)
    return vectorstore


def create_agent(vectorstore):
    llm = ChatOpenAI(model="gpt-5-mini", temperature=0)

    prompt_db = PromptTemplate(
        input_variables=["query", "retrieved_schema"],
        template="""
Select the most relevant database and table to answer the user query.

User query: {query}
Schema info: {retrieved_schema}

Respond ONLY with JSON:
{{
  "database": "...",
  "tables": ["..."],
  "columns": ["..."],
  "reasons": "..."
}}
""",
    )

    db_chain = prompt_db | llm

    def database_selection_agent(user_query: str, top_k: int = 5):
        relevant_docs = vectorstore.similarity_search_with_score(user_query, k=top_k)
        retrieved_schema = "\n".join(
            f"score: {score:.4f}, content: {doc.page_content}"
            for doc, score in relevant_docs
        )

        response = db_chain.invoke({"query": user_query, "retrieved_schema": retrieved_schema})
        raw = response.content if hasattr(response, "content") else str(response)

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"error": "invalid LLM output", "raw": raw}

        return parsed

    return database_selection_agent


def run(api_key, payload: dict):
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

        vectorstore = create_or_load_embeddings()
        agent = create_agent(vectorstore)
        return agent(user_query, top_k=5)

    except Exception as e:
        return {"error": f"Agent A failed: {str(e)}"}
