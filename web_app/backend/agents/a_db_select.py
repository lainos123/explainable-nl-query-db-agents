# from utils.get_keys import get_api_key

# import json
# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate

# llm = ChatOpenAI(model="gpt-5-mini", temperature=0)

# prompt_db = PromptTemplate(
#     input_variables=["query", "retrieved_schema"],
#     template="""
# Please select the most relevant database and table in order to answer user's query.
# User query: {query}
# Schema info: {retrieved_schema}
# Respond ONLY in JSON: {{ "db_name": "...", "tables": ["..."], "columns": ["..."] }}
# """
# )
# db_chain = prompt_db | llm

# def run(user_query, vectorstore, top_k=5):
#     relevant_docs = vectorstore.similarity_search_with_score(user_query, k=top_k)

#     selected_schema = ""
#     for doc, score in relevant_docs:
#         selected_schema += f"score: {score}, content: {doc.page_content}\n"

#     response = db_chain.invoke({
#         "query": user_query,
#         "retrieved_schema": selected_schema
#     })

#     llm_output = response.content if hasattr(response, "content") else str(response)
#     return json.loads(llm_output)

# Agent A specific logic here
def db_select(api_key, request, media_path):
    return {"content": "Agent A DB Selector executed successfully."}