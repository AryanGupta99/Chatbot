"""
Test and compare Regular RAG vs Expert RAG
"""

from src.rag_engine import RAGEngine
from src.expert_rag_engine import ExpertRAGEngine
import time

def test_comparison():
    """Compare regular vs expert RAG responses"""
    
    print("="*70)
    print("INITIALIZING RAG ENGINES")
    print("="*70)
    
    print("\nLoading Regular RAG...")
    regular_rag = RAGEngine()
    
    print("Loading Expert RAG...")
    expert_rag = ExpertRAGEngine()
    
    # Test queries
    test_queries = [
        "I forgot my password, how do I reset it?",
        "My QuickBooks is showing error -6177",
        "I can't connect to Remote Desktop from my Mac",
        "How much does storage upgrade cost?",
        "My server is running very slow",
        "How do I add a new user?",
    ]
    
    for query in test_queries:
        print("\n" + "="*70)
        print(f"QUERY: {query}")
        print("="*70)
        
        # Test Regular RAG
        print("\n" + "-"*70)
        print("REGULAR RAG:")
        print("-"*70)
        start = time.time()
        regular_result = regular_rag.process_query(query)
        regular_time = time.time() - start
        
        print(f"Time: {regular_time:.2f}s")
        print(f"Confidence: {regular_result['confidence']}")
        print(f"Sources: {len(regular_result.get('sources', []))}")
        print(f"\nResponse:\n{regular_result['response']}")
        
        # Test Expert RAG
        print("\n" + "-"*70)
        print("EXPERT RAG:")
        print("-"*70)
        start = time.time()
        expert_result = expert_rag.process_query_expert(query)
        expert_time = time.time() - start
        
        print(f"Time: {expert_time:.2f}s")
        print(f"Category: {expert_result['category']} (conf: {expert_result.get('category_confidence', 0):.2f})")
        print(f"Confidence: {expert_result['confidence']}")
        print(f"Sources: {len(expert_result.get('sources', []))}")
        
        if expert_result.get('retrieval_stats'):
            stats = expert_result['retrieval_stats']
            print(f"Avg Relevance: {stats['avg_relevance']:.2f}")
            print(f"Top Score: {stats['top_score']:.2f}")
        
        print(f"\nResponse:\n{expert_result['response']}")
        
        # Comparison
        print("\n" + "-"*70)
        print("COMPARISON:")
        print("-"*70)
        print(f"Speed: Expert is {regular_time/expert_time:.1f}x {'faster' if expert_time < regular_time else 'slower'}")
        print(f"Response Length: Regular={len(regular_result['response'])} chars, Expert={len(expert_result['response'])} chars")
        
        input("\nPress Enter for next query...")


def test_expert_features():
    """Test expert-specific features"""
    
    print("="*70)
    print("TESTING EXPERT RAG FEATURES")
    print("="*70)
    
    expert_rag = ExpertRAGEngine()
    
    # Test query classification
    print("\n" + "-"*70)
    print("QUERY CLASSIFICATION:")
    print("-"*70)
    
    test_queries = [
        "reset my password",
        "disk space full",
        "quickbooks error -6177",
        "can't connect rdp",
        "email not working",
        "server is slow"
    ]
    
    for query in test_queries:
        category, confidence = expert_rag.classify_query(query)
        print(f"{query:40} → {category:20} (conf: {confidence:.2f})")
    
    # Test keyword extraction
    print("\n" + "-"*70)
    print("KEYWORD EXTRACTION:")
    print("-"*70)
    
    test_queries = [
        "How do I reset my password on the SelfCare portal?",
        "QuickBooks multi-user mode error -6098 when opening company file",
        "Remote Desktop connection keeps disconnecting on Mac"
    ]
    
    for query in test_queries:
        keywords = expert_rag.extract_keywords(query)
        print(f"\nQuery: {query}")
        print(f"Keywords: {', '.join(keywords)}")
    
    # Test advanced retrieval
    print("\n" + "-"*70)
    print("ADVANCED RETRIEVAL:")
    print("-"*70)
    
    query = "QuickBooks error -6177"
    results = expert_rag.retrieve_context_advanced(query, category="quickbooks")
    
    print(f"\nQuery: {query}")
    print(f"Retrieved: {len(results)} results")
    print("\nTop 3 Results:")
    for i, result in enumerate(results[:3], 1):
        print(f"\n{i}. {result['id']}")
        print(f"   Category: {result['metadata'].get('category')}")
        print(f"   Combined Score: {result.get('combined_score', 0):.3f}")
        print(f"   Content: {result['content'][:100]}...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "features":
        test_expert_features()
    else:
        test_comparison()
