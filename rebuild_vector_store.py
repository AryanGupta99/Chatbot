"""
Rebuild Vector Store with All Chunks
This script will properly load all 925 chunks into the vector store
"""

import json
import shutil
from pathlib import Path
from src.vector_store import VectorStore
from config import settings

def rebuild_vector_store():
    """Rebuild vector store from scratch with all chunks"""
    
    print("="*70)
    print("REBUILDING VECTOR STORE")
    print("="*70)
    
    # Step 1: Load chunks
    chunks_file = Path("data/processed/final_chunks.json")
    
    if not chunks_file.exists():
        print("❌ Error: final_chunks.json not found!")
        print("Run: python src/data_processor.py && python src/chunker.py")
        return False
    
    print(f"\n[1/4] Loading chunks from {chunks_file}...")
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"✅ Loaded {len(chunks)} chunks")
    
    # Show breakdown
    doc_chunks = [c for c in chunks if c['metadata'].get('type') != 'training_example']
    training_chunks = [c for c in chunks if c['metadata'].get('type') == 'training_example']
    
    print(f"   - Document chunks: {len(doc_chunks)}")
    print(f"   - Training examples: {len(training_chunks)}")
    
    # Step 2: Delete existing vector store
    chroma_dir = Path(settings.chroma_persist_directory)
    
    if chroma_dir.exists():
        print(f"\n[2/4] Deleting existing vector store at {chroma_dir}...")
        try:
            shutil.rmtree(chroma_dir)
            print("✅ Deleted old vector store")
        except Exception as e:
            print(f"⚠️  Warning: Could not delete old store: {e}")
            print("   Continuing anyway...")
    else:
        print(f"\n[2/4] No existing vector store found (this is fine)")
    
    # Step 3: Create new vector store
    print(f"\n[3/4] Creating new vector store...")
    vector_store = VectorStore()
    vector_store.create_collection()
    print("✅ Created new collection")
    
    # Step 4: Add all chunks
    print(f"\n[4/4] Adding {len(chunks)} chunks to vector store...")
    print("⏳ This will take a few minutes (generating embeddings)...")
    
    try:
        vector_store.add_documents(chunks)
        print("✅ Successfully added all chunks!")
    except Exception as e:
        print(f"❌ Error adding documents: {e}")
        return False
    
    # Step 5: Verify
    print(f"\n{'='*70}")
    print("VERIFICATION")
    print("="*70)
    
    stats = vector_store.get_collection_stats()
    print(f"Total documents in vector store: {stats['total_documents']}")
    print(f"Expected: {len(chunks)}")
    
    if stats['total_documents'] == len(chunks):
        print("✅ SUCCESS! All chunks loaded correctly.")
    else:
        print(f"⚠️  WARNING: Mismatch! Expected {len(chunks)}, got {stats['total_documents']}")
    
    # Test search
    print(f"\n{'='*70}")
    print("TESTING SEARCH")
    print("="*70)
    
    test_query = "How do I reset my password?"
    print(f"\nQuery: {test_query}")
    
    results = vector_store.search(test_query, top_k=5)
    print(f"Found {len(results)} results:")
    
    for i, result in enumerate(results, 1):
        similarity = 1 - result['distance'] if result.get('distance') else 1.0
        doc_type = result['metadata'].get('type', 'document')
        category = result['metadata'].get('category', 'N/A')
        
        print(f"\n  [{i}] Similarity: {similarity:.3f} | Type: {doc_type} | Category: {category}")
        print(f"      ID: {result['id']}")
        print(f"      Preview: {result['content'][:100]}...")
    
    # Check if training examples are being retrieved
    training_found = any(r['metadata'].get('type') == 'training_example' for r in results)
    
    if training_found:
        print(f"\n✅ Training examples ARE being retrieved!")
    else:
        print(f"\n⚠️  No training examples in top 5 results")
        print(f"   This might be normal if document chunks are more relevant")
    
    print(f"\n{'='*70}")
    print("REBUILD COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Update your .env file with a valid OpenAI API key")
    print("2. Test the chatbot: python test_chatbot.py")
    print("3. Check if responses are now using the knowledge base")
    
    return True

if __name__ == "__main__":
    success = rebuild_vector_store()
    
    if not success:
        print("\n❌ Rebuild failed. Check errors above.")
        exit(1)
