"""Test Disk Storage Knowledge"""
from src.rag_engine import RAGEngine

print("="*70)
print("TESTING DISK STORAGE KNOWLEDGE")
print("="*70)

rag = RAGEngine()

queries = [
    "My C drive is showing red, what should I do?",
    "I need more storage space",
    "How much does storage upgrade cost?",
    "My disk is full"
]

for i, q in enumerate(queries, 1):
    print(f"\n{'='*70}")
    print(f"Query {i}: {q}")
    print(f"{'='*70}")
    
    result = rag.process_query(q)
    response = result['response']
    print(f"\n{response}\n")
    
    # Check for key elements
    if "cleanup" in response.lower() or "temp" in response.lower():
        print("✓ Mentions cleanup steps")
    if "$" in response and ("40" in response or "60" in response):
        print("✓ Includes pricing")
    if "ticket" in response.lower():
        print("✓ Mentions ticket creation")
