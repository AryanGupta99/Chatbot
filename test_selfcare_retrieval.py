"""
Test SelfCare Portal Content Retrieval
"""

from src.vector_store import VectorStore

def test_selfcare_retrieval():
    """Test if SelfCare content is in vector store"""
    
    print("="*70)
    print("TESTING SELFCARE PORTAL CONTENT IN VECTOR STORE")
    print("="*70)
    
    # Initialize vector store
    print("\n[1/2] Initializing vector store...")
    vs = VectorStore()
    vs.create_collection()
    print("✅ Vector store initialized")
    
    # Get stats
    stats = vs.get_collection_stats()
    print(f"\nVector Store Stats:")
    print(f"  Total documents: {stats['total_documents']}")
    
    # Test queries
    test_queries = [
        "SelfCare Portal password reset",
        "Google Authenticator enrollment",
        "https://Selfcare.acecloudhosting.com",
        "forgot password enrollment required"
    ]
    
    print(f"\n[2/2] Testing {len(test_queries)} retrieval queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Query {i}: {query}")
        print(f"{'='*70}")
        
        results = vs.search(query, top_k=3)
        
        if results:
            print(f"\n✅ Found {len(results)} results")
            for j, result in enumerate(results, 1):
                distance = result.get('distance', 0)
                similarity = 1 - distance if distance else 1.0
                category = result['metadata'].get('category', 'Unknown')
                doc_id = result['metadata'].get('doc_id', 'Unknown')
                
                print(f"\nResult {j}:")
                print(f"  Similarity: {similarity:.2%}")
                print(f"  Category: {category}")
                print(f"  Doc ID: {doc_id}")
                print(f"  Content preview: {result['content'][:200]}...")
                
                # Check for SelfCare keywords
                content_lower = result['content'].lower()
                if "selfcare" in content_lower or "self care" in content_lower:
                    print("  ✓ Contains SelfCare reference")
                if "google authenticator" in content_lower:
                    print("  ✓ Contains Google Authenticator reference")
                if "acecloudhosting.com" in content_lower:
                    print("  ✓ Contains portal URL")
        else:
            print("\n❌ No results found")
    
    print(f"\n{'='*70}")
    print("Testing complete!")
    print(f"{'='*70}")

if __name__ == "__main__":
    test_selfcare_retrieval()
