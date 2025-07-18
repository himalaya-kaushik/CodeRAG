# file: chatbot.py

import json
import datetime
import chromadb
from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFaceEmbeddings
from summary_generator import generate_codebase_summary
from query_classifier import classify_query

# Load parsed codebase
with open("parsed_code.json", "r", encoding="utf-8") as f:
    parsed_data = json.load(f)

# Load model config
try:
    with open("model_config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {
        "model_name": "phi3:3b",
        "temperature": 0.1,
        "max_tokens": 1024,
        "ollama_host": "http://localhost:11434"
    }
    print("⚠️ No model_config.json found. Using default config with phi3:3b.")

print(f"✅ Using Ollama model: {config['model_name']}")

# Warn user if they're using a large model
if "codellama" in config["model_name"].lower():
    print("""
⚠️ WARNING:
You are using codellama-7b. This requires ~10-12 GB RAM.
On a 16 GB machine, it might crash your system.
Consider switching to phi3:3b for testing.
""")

# Initialize Ollama LLM
llm = Ollama(
    model=config["model_name"],
    temperature=config["temperature"],
    base_url=config["ollama_host"]
)

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection(name="codebase")

# Initialize embeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Function to log each query
def log_query(query: str, results: list):
    with open("query_log.txt", "a", encoding="utf-8") as log:
        log.write(f"{datetime.datetime.now()} :: '{query}' → {len(results)} results\n")

# Search ChromaDB for code snippets
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
            "code": search_results["documents"][0][i][:2000],   # truncate long code
            "preceding_comments": json.loads(meta.get("preceding_comments", "[]"))
        })

    return results

# Handle user question
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

    try:
        response = llm.invoke(prompt)
    except Exception as e:
        response = f"❌ Error invoking LLM: {e}\nYour model might be too large for your system. Try a smaller model like phi3:3b."

    return response

# CLI chat loop
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
