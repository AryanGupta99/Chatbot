"""Test what's being retrieved from the vector store"""
from src.rag_engine import RAGEngine
import json

# Initialize RAG engine
rag = RAGEngine()

# Test queries
test_queries = [
    "How do I reset my password?",
    "QuickBooks error -6177",
    "I can't connect to Remote Desktop",
    "My email is not working"
]

print("="*70)
print("TESTING RAG RETRIEVAL")
print("="*70)

for query in test_queries:
    print(f"\n\n{'='*70}")
    print(f"QUERY: {query}")
    print("="*70)
    
    # Get retrieved context
    results = rag.retrieve_context(query, top_k=5)
    
    print(f"\nRetrieved {len(results)} results:")
    print("-"*70)
    
    for i, result in enumerate(results, 1):
        distance = result.get('distance', 0)
        similarity = 1 - distance if distance else 1.0
        
        print(f"\n[Result {i}] Similarity: {similarity:.3f}")
        print(f"ID: {result['id']}")
        print(f"Category: {result['metadata'].get('category', 'N/A')}")
        print(f"Source: {result['metadata'].get('source', 'N/A')}")
        print(f"Type: {result['metadata'].get('type', 'document')}")
        print(f"Content preview: {result['content'][:200]}...")
    
    # Test full query processing
    print(f"\n\n{'='*70}")
    print("FULL RESPONSE:")
    print("="*70)
    
    response = rag.process_query(query)
    print(f"\nEscalate: {response['escalate']}")
    print(f"Confidence: {response['confidence']}")
    print(f"\nResponse:\n{response['response']}")
    
    input("\nPress Enter to continue to next query...")

print("\n\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
