import chromadb
import ollama
from langchain_huggingface import HuggingFaceEmbeddings

# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection(name="codebase")

# Load Embedding Model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def search_codebase(query: str, top_k=7):
    """Retrieve top K relevant code snippets based on query"""
    query_embedding = embedding_model.embed_query(query)

    search_results = chroma_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["metadatas", "documents"]
    )

    if not search_results["ids"][0]:
        return None
    
    results = []
    for i in range(len(search_results["ids"][0])):
        results.append({
            "name": search_results["metadatas"][0][i]["name"],
            "file": search_results["metadatas"][0][i]["file"],
            "code": search_results["documents"][0][i]
        })
    
    return results

def ask_ollama_about_code(query: str):
    """Retrieve relevant code and ask Ollama for an explanation or modification."""
    
    # Retrieve relevant code from ChromaDB
    code_snippets = search_codebase(query)

    if not code_snippets:
        return "❌ No relevant code found."

    formatted_code = "\n\n".join(
        [f"📌 Function: {c['name']}\n📄 File: {c['file']}\n```python\n{c['code']}\n```" for c in code_snippets]
    )

    # **More Specific Prompt for Ollama**
    ollama_prompt = f"""
    You are a senior Python developer with expertise in data processing and music analysis.

    The user has asked: **{query}**
    
    **Here is the function code that needs modification:**
    {formatted_code}

    **Task:** Modify the function to support MP3 files.
    - The function currently loads audio using `librosa.load()`
    - Modify it to use `pydub` or another suitable library for MP3 support.
    - Return the **modified Python function** without any additional explanation.
    """

    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": ollama_prompt}])
    return response['message']['content']

def chat_with_codebase():
    print("\n💬 Chat with Your Codebase (type 'exit' to stop)\n")

    while True:
        user_query = input("📝 You: ")
        if user_query.lower() == "exit":
            print("👋 Exiting chat.")
            break

        response = ask_ollama_about_code(user_query)
        print("\n🤖 Llama 3.2:\n", response, "\n")

# Run chatbot
chat_with_codebase()
