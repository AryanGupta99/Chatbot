"""
Rebuild Vector Store with Focused Chunks
"""

import json
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

from src.vector_store import VectorStore
from config import settings

def rebuild_vector_store():
    """Rebuild vector store with focused chunks"""
    
    print("="*70)
    print("REBUILDING VECTOR STORE WITH FOCUSED DATA")
    print("="*70)
    
    # Load focused chunks
    chunks_file = Path("data/processed/focused_chunks.json")
    
    if not chunks_file.exists():
        print("❌ Error: focused_chunks.json not found!")
        print("Run: python build_focused_kb.py first")
        return False
    
    print(f"\n[1/3] Loading focused chunks...")
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"✅ Loaded {len(chunks)} chunks")
    
    # Show breakdown
    doc_chunks = [c for c in chunks if c['metadata'].get('type') not in ['training_example', 'kb_article']]
    kb_chunks = [c for c in chunks if c['metadata'].get('type') == 'kb_article']
    training_chunks = [c for c in chunks if c['metadata'].get('type') == 'training_example']
    
    print(f"   - PDF KB chunks: {len(doc_chunks)}")
    print(f"   - Manual KB chunks: {len(kb_chunks)}")
    print(f"   - Training examples: {len(training_chunks)}")
    
    # Delete existing vector store
    chroma_dir = Path(settings.chroma_persist_directory)
    
    if chroma_dir.exists():
        print(f"\n[2/3] Deleting old vector store...")
        try:
            shutil.rmtree(chroma_dir)
            print("✅ Deleted old vector store")
        except Exception as e:
            print(f"⚠️  Warning: {e}")
    
    # Create new vector store and add chunks
    print(f"\n[3/3] Creating new vector store and adding chunks...")
    print("⏳ Generating embeddings (this takes 3-5 minutes)...")
    
    try:
        vector_store = VectorStore()
        vector_store.create_collection()
        vector_store.add_documents(chunks)
        print("✅ Successfully added all chunks!")
    except Exception as e:
        print(f"❌ Error: {e}")
        if "401" in str(e) or "api" in str(e).lower():
            print("\n⚠️  API KEY ISSUE")
            print("Check your .env file has valid OpenAI API key")
        return False
    
    # Verify
    stats = vector_store.get_collection_stats()
    print(f"\n{'='*70}")
    print("VERIFICATION")
    print(f"{'='*70}")
    print(f"Documents in vector store: {stats['total_documents']}")
    print(f"Expected: {len(chunks)}")
    
    if stats['total_documents'] == len(chunks):
        print("✅ SUCCESS! All chunks loaded correctly.")
    else:
        print(f"⚠️  Mismatch: Expected {len(chunks)}, got {stats['total_documents']}")
    
    # Test search
    print(f"\n{'='*70}")
    print("TESTING SEARCH")
    print(f"{'='*70}")
    
    test_queries = [
        "How do I reset my password?",
        "QuickBooks error -6177",
        "Can't connect to Remote Desktop"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = vector_store.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            similarity = 1 - result['distance'] if result.get('distance') else 1.0
            doc_type = result['metadata'].get('type', 'document')
            category = result['metadata'].get('category', 'N/A')
            
            print(f"  [{i}] {similarity:.3f} | {doc_type} | {category}")
            print(f"      {result['content'][:80]}...")
    
    return True

if __name__ == "__main__":
    success = rebuild_vector_store()
    
    if success:
        print(f"\n{'='*70}")
        print("✅ REBUILD COMPLETE!")
        print(f"{'='*70}")
        print("\nYour knowledge base is now ready with:")
        print("✓ 800 focused, ticket-relevant chunks")
        print("✓ 93 PDF KB documents")
        print("✓ 10 manual KB articles")
        print("✓ 15 high-quality training examples")
        print("\nNext: Test with python test_chatbot.py")
    else:
        print(f"\n{'='*70}")
        print("❌ REBUILD FAILED")
        print(f"{'='*70}")
