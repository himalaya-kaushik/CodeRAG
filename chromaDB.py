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

with open("parsed_code.json", "r", encoding="utf-8") as f:
    parsed_data = json.load(f)

chroma_client = chromadb.PersistentClient(path="./chroma_db")  # ✅ Auto-persistence
chroma_collection = chroma_client.get_or_create_collection(name="codebase")

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

batch_size = 500  
documents = []
ids = set()  
batch_counter = 0

readme_content = parsed_data.get("README", "")
if readme_content:
    readme_metadata = {
        "file": "README.md",
        "name": "Project README",
        "docstring": "README provides an overview of the project."
    }
    documents.append({"id": "README", "content": readme_content, "metadata": readme_metadata})
    ids.add("README")

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

if documents:
    batch_counter += 1
    print(f"🚀 Storing Final Batch {batch_counter} ({len(documents)} docs)...")
    chroma_collection.add(
        ids=[doc["id"] for doc in documents],
        documents=[doc["content"] for doc in documents],
        metadatas=[doc["metadata"] for doc in documents]
    )

print(f"✅ Successfully stored all {batch_counter} batches in ChromaDB!")

stored_count = chroma_collection.count()
print(f"🔍 Immediate Count Check: {stored_count} documents stored in ChromaDB.")

