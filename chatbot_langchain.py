# file: chatbot.py

import json
import datetime
import chromadb
from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFaceEmbeddings
from summary_generator import generate_codebase_summary
from query_classifier import classify_query
from history import (
    get_project_id,
    get_history_path,
    load_chat_history,
    save_chat_history,
    append_message,
    delete_chat_history
)
from cache import (
    load_cache,
    save_cache,
    get_cached_response,
    set_cached_response
)
from context_builder import summarize_history, format_recent_turns

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
def ask_codebuddy(query: str, parsed_data: dict, chat_history: list, cache: dict) -> str:
    # 🔍 Check cache first
    cached = get_cached_response(cache, query)
    if cached:
        return f"(cached)\n{cached}"

    query_type = classify_query(query)

    if query_type == "overview":
        summary = generate_codebase_summary(parsed_data)
        context = summary
    else:
        code_snippets = search_codebase(query, top_k=7)
        log_query(query, code_snippets)

        context = "\n\n".join([
            f"📌 {c['name']} ({c['file']})\n"
            f"💬 Comments: {' | '.join(c['preceding_comments'])}\n"
            f"```python\n{c['code']}\n```"
            for c in code_snippets
        ])

    memory_summary = summarize_history(llm, chat_history)
    recent_dialogue = format_recent_turns(chat_history)

    system_prefix = {
        "overview": "You are a senior Python software engineer.",
        "suggestion": "You are an expert Python code reviewer.",
        "function": "You are a Python code assistant."
    }.get(query_type, "You are a helpful assistant.")

    prompt = f"""{system_prefix}

# Context:
{context}

# Summary of previous chat:
{memory_summary}

# Recent conversation:
{recent_dialogue}

# Current question:
User: {query}
Assistant:"""

    try:
        response = llm.invoke(prompt)
    except Exception as e:
        response = f"❌ Error invoking LLM: {e}\nYour model might be too large for your system. Try a smaller model like phi3:3b."

    # 💾 Cache response
    set_cached_response(cache, query, response)

    return response

# CLI chat loop
def chat_with_codebase():
    project_id = get_project_id()
    history_path = get_history_path(project_id)
    chat_history = load_chat_history(history_path)
    cache = load_cache(project_id)

    print("\n💬 Welcome to CodeBuddy! (type 'exit' to quit)\n")

    if chat_history:
        print("📜 Restored previous session:\n")
        for h in chat_history[-2:]:
            print(f"📝 You: {h['user']}")
            print(f"🤖 CodeBuddy: {h['assistant']}\n")

    while True:
        query = input("📝 You: ")
        if query.strip().lower() == "exit":
            print("👋 Exiting CodeBuddy. Chat history saved.")
            break
        if query.strip().lower() == "delete history":
            confirmed = input("⚠️ This will erase your current session. Type 'yes' to confirm: ")
            if confirmed.lower() == "yes":
                chat_history.clear()
                deleted = delete_chat_history(history_path)
                msg = "🧹 History cleared from memory and disk." if deleted else "⚠️ Memory cleared, but file not found."
                print(msg)
            else:
                print("❌ Cancelled. History not deleted.")
            continue

        response = ask_codebuddy(query, parsed_data, chat_history, cache)
        print("\n🤖 CodeBuddy:\n", response)

        chat_history = append_message(chat_history, query, response)
        save_chat_history(history_path, chat_history)
        save_cache(project_id, cache)

if __name__ == "__main__":
    chat_with_codebase()
