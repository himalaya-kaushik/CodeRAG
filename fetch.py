import chromadb

chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection(name="codebase")

query = "Data.make_raw_data"  
search_results = chroma_collection.get(
    where={"name": {"$in": [query]}},  
    include=["metadatas", "documents"],
    limit=5
)

print(f"✅ Found {len(search_results['ids'])} results for '{query}':\n")
for i in range(len(search_results["ids"])):
    print(f"\n🔹 **Result {i+1}:**")
    print(f"ID: {search_results['ids'][i]}")
    print(f"Metadata: {search_results['metadatas'][i]}")
    print(f"Code:\n{search_results['documents'][i][:300]}...") 