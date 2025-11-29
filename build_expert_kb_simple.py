"""
Simple Expert KB Builder - Windows Compatible
"""

import json
from pathlib import Path
from src.vector_store import VectorStore

def build_from_existing():
    """Build vector store from existing chunks"""
    print("="*70)
    print("BUILDING EXPERT VECTOR STORE FROM EXISTING CHUNKS")
    print("="*70)
    
    # Load existing chunks
    chunks_file = Path("data/expert_kb/expert_kb_chunks.json")
    
    if not chunks_file.exists():
        print("ERROR: expert_kb_chunks.json not found!")
        print("Please run the full build first to create chunks.")
        return
    
    print("\nLoading chunks...")
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} chunks")
    
    # Build vector store
    print("\nBuilding vector store...")
    vector_store = VectorStore()
    vector_store.create_collection()
    vector_store.add_documents(chunks)
    
    print("\n" + "="*70)
    print("COMPLETE! Vector store is ready.")
    print("="*70)
    
    # Test search
    print("\nTesting search...")
    test_query = "How do I reset my password?"
    results = vector_store.search(test_query, top_k=3)
    
    print(f"\nQuery: {test_query}")
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['id']}")
        print(f"   Category: {result['metadata'].get('category', 'Unknown')}")
        print(f"   Distance: {result.get('distance', 0):.3f}")
        print(f"   Content: {result['content'][:100]}...")

if __name__ == "__main__":
    build_from_existing()
