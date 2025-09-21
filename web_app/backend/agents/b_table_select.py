# from utils.get_keys import get_api_key

# import json
# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate

# llm = ChatOpenAI(model="gpt-5-mini", temperature=0)

# list_tables_prompt = PromptTemplate(
#     input_variables=["user_query", "db_schema_json"],
#     template=(
#         "Given the selected database schema, return ONLY valid JSON:\n"
#         '{ "relevant_tables": ["..."], "reasons": "..." }\n\n'
#         "User query: {user_query}\n"
#         "DB schema JSON: {db_schema_json}\n"
#     ),
# )
# db_chain_2 = list_tables_prompt | llm

# def run(user_query, db_schema_json):
#     response = db_chain_2.invoke({
#         "user_query": user_query,
#         "db_schema_json": db_schema_json
#     })
#     llm_output = response.content if hasattr(response, "content") else str(response)
#     return json.loads(llm_output)


# Agent B specific logic here
def table_select(api_key, request, media_path):
    return {"content": "Agent B executed successfully."}