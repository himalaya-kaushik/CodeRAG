# import chromadb

# # Step 1: Connect to ChromaDB
# chroma_client = chromadb.PersistentClient(path="./chroma_db")
# chroma_collection = chroma_client.get_or_create_collection(name="codebase")

# # Step 2: Check Stored Document Count
# stored_count = chroma_collection.count()
# print(f"✅ Total Documents Stored: {stored_count}")

# # Step 3: Retrieve Sample Data
# if stored_count > 0:
#     docs = chroma_collection.get(include=["metadatas", "documents"], limit=5)

#     print("\n🔹 **Sample Stored Documents:**")
#     for i in range(len(docs["ids"])):
#         print(f"\n🔹 **Document {i+1}:**")
#         print(f"ID: {docs['ids'][i]}")
#         print(f"Metadata: {docs['metadatas'][i]}")
#         print(f"Content: {docs['documents'][i][:200]}...")  # Print first 200 chars
# else:
#     print("❌ No documents found. ChromaDB might not be persisting data.")

import chromadb

# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection(name="codebase")

# Retrieve all documents
search_results = chroma_collection.get(
    include=["metadatas"],
    limit=100  # Limit to avoid too much data
)

# Print all function/class names stored
print("🔍 Stored Functions in ChromaDB:\n")
for meta in search_results["metadatas"]:
    print(meta["name"])
