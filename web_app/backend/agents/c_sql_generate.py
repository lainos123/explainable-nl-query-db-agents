# from utils.get_keys import get_api_key

# import json
# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate

# llm = ChatOpenAI(model="gpt-5-mini", temperature=0)

# produce_sql_prompt = PromptTemplate(
#     input_variables=["user_query", "db_schema_json", "selected_tables"],
#     template=(
#         "Given the schema and selected tables, return ONLY JSON:\n"
#         '{ "relevant_tables": ["..."], "SQL Code": "...", "reasons": "..." }\n\n'
#         "User query: {user_query}\n"
#         "DB schema JSON: {db_schema_json}\n"
#         "Selected tables: {selected_tables}\n"
#     ),
# )
# db_chain_3 = produce_sql_prompt | llm

# def run(user_query, db_schema_json, selected_tables):
#     response = db_chain_3.invoke({
#         "user_query": user_query,
#         "db_schema_json": db_schema_json,
#         "selected_tables": selected_tables
#     })
#     llm_output = response.content if hasattr(response, "content") else str(response)
#     return json.loads(llm_output)

# Agent C specific logic here
def sql_generate(api_key, request, media_path):
    return {"content": "Agent C SQL Generate executed successfully."}