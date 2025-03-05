import chromadb

# Step 1: Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection(name="codebase")

# Step 2: Query ChromaDB for Matching Function Names
query = "Data.make_raw_data"  # 🔍 Change this to any keyword
search_results = chroma_collection.get(
    where={"name": {"$in": [query]}},  # ✅ Use `$in` instead of `$contains`
    include=["metadatas", "documents"],
    limit=5
)

# Step 3: Print Results
print(f"✅ Found {len(search_results['ids'])} results for '{query}':\n")
for i in range(len(search_results["ids"])):
    print(f"\n🔹 **Result {i+1}:**")
    print(f"ID: {search_results['ids'][i]}")
    print(f"Metadata: {search_results['metadatas'][i]}")
    print(f"Code:\n{search_results['documents'][i][:300]}...")  # Show first 300 chars
