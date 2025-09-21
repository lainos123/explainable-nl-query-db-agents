# TEST
def schema_graph():
    return {"message": "Test successful"}


def run(request, media_path: str):
    """
    Django endpoint function for schema graph
    """
    try:
        result = schema_graph()
        return {"success": True, "result": result}
    except Exception as e:
        return {"error": f"Schema graph failed: {str(e)}"}