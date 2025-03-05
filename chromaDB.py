# import chromadb

# # Step 1: Initialize ChromaDB with Persistent Storage
# chroma_client = chromadb.PersistentClient(path="./chroma_db")  # ✅ Ensures automatic persistence
# chroma_collection = chroma_client.get_or_create_collection(name="test_collection")

# # Step 2: Insert Dummy Data
# dummy_data = [
#     {"id": "doc1", "content": "This is the first test document.", "metadata": {"category": "test"}},
#     {"id": "doc2", "content": "Here is another document with different content.", "metadata": {"category": "test"}},
#     {"id": "doc3", "content": "Final test document for checking ChromaDB.", "metadata": {"category": "test"}}
# ]

# # Step 3: Store in ChromaDB
# chroma_collection.add(
#     ids=[doc["id"] for doc in dummy_data],
#     documents=[doc["content"] for doc in dummy_data],
#     metadatas=[doc["metadata"] for doc in dummy_data]
# )

# print("✅ Dummy data inserted successfully!")


import json
import hashlib
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# Step 1: Load the Parsed Code JSON
with open("parsed_code.json", "r", encoding="utf-8") as f:
    parsed_data = json.load(f)

# Step 2: Initialize ChromaDB in Local Directory
chroma_client = chromadb.PersistentClient(path="./chroma_db")  # ✅ Auto-persistence
chroma_collection = chroma_client.get_or_create_collection(name="codebase")

# Step 3: Set Up Sentence Transformer for Embeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Step 4: Store Each Function/Class in ChromaDB
batch_size = 500  # ✅ Store in batches
documents = []
ids = set()  # Track unique IDs
batch_counter = 0

# 📌 4A: Store README as a Document
readme_content = parsed_data.get("README", "")
if readme_content:
    readme_metadata = {
        "file": "README.md",
        "name": "Project README",
        "docstring": "README provides an overview of the project."
    }
    documents.append({"id": "README", "content": readme_content, "metadata": readme_metadata})
    ids.add("README")

# 📌 4B: Store Each Function/Class from Codebase
for file_path, details in parsed_data["parsed_code"].items():
    for func in details["functions_classes"]:
        unique_id = hashlib.md5(f"{file_path}::{func['name']}::{func['start_line']}".encode()).hexdigest()

        if unique_id in ids:
            continue  # Skip duplicates

        ids.add(unique_id)

        metadata = {
            "file": file_path,
            "name": func["name"],
            "start_line": func["start_line"],
            "end_line": func["end_line"],
            "docstring": func.get("docstring", "") or "",
            "calls": json.dumps(func.get("calls", [])),
            "inline_comments": json.dumps(func.get("inline_comments", []))
        }

        documents.append({"id": unique_id, "content": func["code"], "metadata": metadata})

        # ✅ Insert in batches
        if len(documents) >= batch_size:
            batch_counter += 1
            print(f"🚀 Storing Batch {batch_counter} ({len(documents)} docs)...")
            chroma_collection.add(
                ids=[doc["id"] for doc in documents],
                documents=[doc["content"] for doc in documents],
                metadatas=[doc["metadata"] for doc in documents]
            )
            documents.clear()
            ids.clear()  # Reset set

# Step 5: Store Remaining Documents
if documents:
    batch_counter += 1
    print(f"🚀 Storing Final Batch {batch_counter} ({len(documents)} docs)...")
    chroma_collection.add(
        ids=[doc["id"] for doc in documents],
        documents=[doc["content"] for doc in documents],
        metadatas=[doc["metadata"] for doc in documents]
    )

print(f"✅ Successfully stored all {batch_counter} batches in ChromaDB!")

# ✅ Verify Stored Data
stored_count = chroma_collection.count()
print(f"🔍 Immediate Count Check: {stored_count} documents stored in ChromaDB.")

