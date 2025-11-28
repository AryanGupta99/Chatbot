"""Quick password reset test"""
from src.rag_engine import RAGEngine

rag = RAGEngine()

queries = [
    "I forgot my password",
    "How do I enroll in the SelfCare portal?"
]

for q in queries:
    print(f"\n{'='*70}")
    print(f"Q: {q}")
    print(f"{'='*70}")
    result = rag.process_query(q)
    print(result['response'])
    print()
