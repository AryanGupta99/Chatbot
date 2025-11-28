"""Test Disk Storage Responses"""
from src.rag_engine import RAGEngine

rag = RAGEngine()

queries = [
    "My disk is full",
    "C drive showing red",
    "How much does storage upgrade cost?"
]

for q in queries:
    print(f"\n{'='*70}")
    print(f"Q: {q}")
    print(f"{'='*70}")
    result = rag.process_query(q)
    print(result['response'][:600])
    print("\n...")
