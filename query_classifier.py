def classify_query(query: str) -> str:
    query = query.lower()
    if any(x in query for x in ["architecture", "overview", "purpose", "structure", "codebase","summary","whole codebase"]):
        return "overview"
    elif any(x in query for x in ["improve", "refactor", "optimize", "suggest", "rewrite"]):
        return "suggestion"
    else:
        return "function"