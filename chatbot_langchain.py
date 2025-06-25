# file: chatbot.py

import json
import datetime
import chromadb
from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFaceEmbeddings
from summary_generator import generate_codebase_summary
from query_classifier import classify_query

with open("parsed_code.json", "r", encoding="utf-8") as f:
    parsed_data = json.load(f)

chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection(name="codebase")

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

llm = Ollama(model="codellama:7b")

def log_query(query: str, results: list):
    with open("query_log.txt", "a", encoding="utf-8") as log:
        log.write(f"{datetime.datetime.now()} :: '{query}' → {len(results)} results\n")

def search_codebase(query: str, top_k: int = 5):
    query_embedding = embedding_model.embed_query(query)
    search_results = chroma_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["metadatas", "documents"]
    )

    if not search_results["ids"][0]:
        return []

    results = []
    for i in range(len(search_results["ids"][0])):
        meta = search_results["metadatas"][0][i]
        results.append({
            "name": meta.get("name", ""),
            "file": meta.get("file", ""),
            "code": search_results["documents"][0][i],
            "preceding_comments": json.loads(meta.get("preceding_comments", "[]"))
        })

    return results

def ask_codebuddy(query: str, parsed_data: dict) -> str:
    query_type = classify_query(query)

    if query_type == "overview":
        summary = generate_codebase_summary(parsed_data)
        prompt = f"""
You are a senior Python software engineer.

# User Question:
{query}

# Codebase Summary:
{summary}

Please analyze and respond accordingly.
"""
    else:
        code_snippets = search_codebase(query, top_k=7)
        log_query(query, code_snippets)

        if not code_snippets:
            return "🔍 No relevant code found in current context.\nTry rephrasing or ask for a summary."

        formatted = "\n\n".join([
            f"📌 {c['name']} ({c['file']})\n"
            f"💬 Comments: {' | '.join(c['preceding_comments'])}\n"
            f"```python\n{c['code']}\n```"
            for c in code_snippets
        ])

        if query_type == "suggestion":
            prompt = f"""
You are an expert Python code reviewer.

# User Question:
{query}

# Relevant Code Snippets:
{formatted}

# Task:
Suggest improvements, optimizations, or refactorings.
"""
        else:
            prompt = f"""
You are a Python code assistant.

# User Question:
{query}

# Relevant Code Snippets:
{formatted}

# Task:
Explain, describe, or fulfill the above request.
"""

    response = llm.invoke(prompt)
    return response

def chat_with_codebase():
    print("\n💬 Welcome to CodeBuddy! (type 'exit' to quit)\n")
    while True:
        query = input("📝 You: ")
        if query.strip().lower() == "exit":
            print(" Exiting CodeBuddy. Bye!")
            break
        response = ask_codebuddy(query, parsed_data)
        print("\n🤖 CodeBuddy:\n", response)

if __name__ == "__main__":
    chat_with_codebase()