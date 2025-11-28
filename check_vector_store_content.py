"""Check what's actually in the vector store"""
import chromadb
from chromadb.config import Settings
from config import settings as app_settings
import json

# Connect to ChromaDB
client = chromadb.PersistentClient(
    path=app_settings.chroma_persist_directory,
    settings=Settings(anonymized_telemetry=False)
)

# Get collection
collection = client.get_collection(name=app_settings.collection_name)

# Get stats
count = collection.count()
print(f"Total documents in collection: {count}")

# Get a sample of documents
sample = collection.get(limit=10, include=['documents', 'metadatas'])

print(f"\n{'='*70}")
print("SAMPLE DOCUMENTS IN VECTOR STORE")
print("="*70)

for i in range(len(sample['ids'])):
    doc_id = sample['ids'][i]
    content = sample['documents'][i]
    metadata = sample['metadatas'][i]
    
    print(f"\n[Document {i+1}]")
    print(f"ID: {doc_id}")
    print(f"Category: {metadata.get('category', 'N/A')}")
    print(f"Source: {metadata.get('source', 'N/A')}")
    print(f"Type: {metadata.get('type', 'document')}")
    print(f"Content length: {len(content)} chars")
    print(f"Content preview: {content[:300]}...")
    print("-"*70)

# Check metadata distribution
all_docs = collection.get(include=['metadatas'])
categories = {}
sources = {}
types = {}

for metadata in all_docs['metadatas']:
    cat = metadata.get('category', 'Unknown')
    src = metadata.get('source', 'Unknown')
    typ = metadata.get('type', 'document')
    
    categories[cat] = categories.get(cat, 0) + 1
    sources[src] = sources.get(src, 0) + 1
    types[typ] = types.get(typ, 0) + 1

print(f"\n{'='*70}")
print("METADATA DISTRIBUTION")
print("="*70)

print(f"\nCategories:")
for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
    print(f"  {cat}: {count}")

print(f"\nSources:")
for src, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
    print(f"  {src}: {count}")

print(f"\nTypes:")
for typ, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {typ}: {count}")
