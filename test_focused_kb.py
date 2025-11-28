"""Test the focused knowledge base"""
from dotenv import load_dotenv
load_dotenv(override=True)

from src.rag_engine import RAGEngine

# Initialize RAG engine
rag = RAGEngine()

print("="*70)
print("TESTING FOCUSED KNOWLEDGE BASE")
print("="*70)

# Test queries based on real tickets
test_queries = [
    "I forgot my password, how do I reset it?",
    "QuickBooks error -6177 when opening company file",
    "Can't connect to Remote Desktop server",
    "Server is running very slow",
    "My email keeps asking for password in Outlook",
    "How do I add a new user to the server?",
    "QuickBooks says maximum number of users exceeded"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*70}")
    print(f"TEST {i}: {query}")
    print("="*70)
    
    # Get response
    result = rag.process_query(query)
    
    print(f"\n📊 Escalate: {result['escalate']}")
    print(f"📊 Confidence: {result['confidence']}")
    print(f"📊 Sources: {len(result.get('sources', []))}")
    
    if result.get('sources'):
        print(f"\n📚 Top Sources:")
        for j, source in enumerate(result['sources'][:3], 1):
            src_type = source.get('category', 'N/A')
            relevance = source.get('relevance', 0)
            print(f"  {j}. {src_type} (relevance: {relevance:.3f})")
    
    print(f"\n💬 Response:")
    print(f"{result['response']}")
    
    print(f"\n{'='*70}")
    input("Press Enter for next test...")

print(f"\n{'='*70}")
print("✅ TESTING COMPLETE")
print("="*70)
print("\nThe knowledge base is now using:")
print("✓ Real KB documentation")
print("✓ Manual curated articles")
print("✓ High-quality training examples")
print("✓ All focused on actual ticket scenarios")
