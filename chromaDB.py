import json
import hashlib
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

# Load parsed data
with open("parsed_code.json", "r", encoding="utf-8") as f:
    parsed_data = json.load(f)

# Init ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection(name="codebase")

# Embedding model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

batch_size = 500
documents = []
ids = set()
batch_counter = 0

# Add README.md if present
readme_content = parsed_data.get("README", "")
if readme_content:
    readme_metadata = {
        "file": "README.md",
        "name": "Project README",
        "docstring": "README provides an overview of the project."
    }
    documents.append({
        "id": "README",
        "content": readme_content.strip(),
        "metadata": readme_metadata
    })
    ids.add("README")

# Iterate parsed code
for file_path, details in parsed_data["parsed_code"].items():
    for item in details["functions_classes"]:
        item_type = item.get("type", "Unknown")

        unique_id = hashlib.md5(f"{file_path}::{item.get('name')}::{item.get('start_line', 1)}".encode()).hexdigest()
        if unique_id in ids:
            continue
        ids.add(unique_id)

        metadata = {
            "file": file_path,
            "name": item.get("name"),
            "type": item_type,
            "start_line": item.get("start_line", 1),
            "end_line": item.get("end_line", 1),
            "docstring": item.get("docstring", "") or "",
            "calls": json.dumps(item.get("calls", [])),
            "inline_comments": json.dumps(item.get("inline_comments", [])),
            "preceding_comments": json.dumps(item.get("preceding_comments", []))
        }

        documents.append({
            "id": unique_id,
            "content": item.get("code", "").strip(),
            "metadata": metadata
        })

        if len(documents) >= batch_size:
            batch_counter += 1
            print(f"\U0001F680 Storing Batch {batch_counter} ({len(documents)} docs)...")
            chroma_collection.add(
                ids=[doc["id"] for doc in documents],
                documents=[doc["content"] for doc in documents],
                metadatas=[doc["metadata"] for doc in documents]
            )
            documents.clear()

# Final batch flush
if documents:
    batch_counter += 1
    print(f"\U0001F680 Storing Final Batch {batch_counter} ({len(documents)} docs)...")
    chroma_collection.add(
        ids=[doc["id"] for doc in documents],
        documents=[doc["content"] for doc in documents],
        metadatas=[doc["metadata"] for doc in documents]
    )

print(f"✅ All {batch_counter} batches stored successfully in ChromaDB!")

# Check count
stored_count = chroma_collection.count()
print(f"\U0001F50D ChromaDB Document Count: {stored_count}")
