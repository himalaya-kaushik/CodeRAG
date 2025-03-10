import json
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

llm = Ollama(model="llama3.2")


def search_codebase(query: str, top_k: int = 5):
    """Retrieve top K relevant code blocks from ChromaDB"""
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
        results.append({
            "name": search_results["metadatas"][0][i].get("name", ""),
            "file": search_results["metadatas"][0][i].get("file", ""),
            "code": search_results["documents"][0][i]
        })

    return results


def ask_codebuddy(query: str, parsed_data: dict) -> str:
    query_type = classify_query(query)

    if query_type == "overview":
        summary = generate_codebase_summary(parsed_data)
        prompt = f"""
You are a senior Python software engineer.

User asked: **{query}**

Here is the full codebase structure summary:
{summary}

Please analyze and answer accordingly.
"""
    else:
        code_snippets = search_codebase(query, top_k=7)
        if not code_snippets:
            return " No relevant code found."

        formatted = "\n\n".join(
            [f"📌 {c['name']} ({c['file']})\n```python\n{c['code']}\n```" for c in code_snippets]
        )

        if query_type == "suggestion":
            prompt = f"""
You are an expert Python code reviewer.

User asked: **{query}**

Here is the relevant code for review:
{formatted}

Please suggest improvements, optimizations, or refactoring suggestions.
"""
        else:
            prompt = f"""
You are a Python code expert.

User asked: **{query}**

Here is the relevant code snippet:
{formatted}

Please explain this in detail or address the query accordingly.
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
