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
import time
def run(api_key, payload, media_path):
    time.sleep(3)
    return {
        "content": "Executed successfully.",
        "previous": payload
    }