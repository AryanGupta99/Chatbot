"""
Pre-Deployment Test Suite
Tests Expert RAG system before pushing to Render
"""

from src.expert_rag_engine import ExpertRAGEngine
from src.vector_store import VectorStore
import time

def test_vector_store():
    """Test vector store is working"""
    print("\n" + "="*70)
    print("TEST 1: Vector Store")
    print("="*70)
    
    try:
        vs = VectorStore()
        vs.create_collection()
        stats = vs.get_collection_stats()
        
        print(f"Collection: {stats['collection_name']}")
        print(f"Total Documents: {stats['total_documents']}")
        
        if stats['total_documents'] > 0:
            print("PASS: Vector store has documents")
            return True
        else:
            print("FAIL: Vector store is empty")
            return False
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_expert_rag_init():
    """Test Expert RAG initialization"""
    print("\n" + "="*70)
    print("TEST 2: Expert RAG Initialization")
    print("="*70)
    
    try:
        rag = ExpertRAGEngine()
        print("PASS: Expert RAG initialized successfully")
        return True, rag
    except Exception as e:
        print(f"FAIL: {e}")
        return False, None

def test_query_classification(rag):
    """Test query classification"""
    print("\n" + "="*70)
    print("TEST 3: Query Classification")
    print("="*70)
    
    test_cases = [
        ("I forgot my password", "password_reset"),
        ("QuickBooks error -6177", "quickbooks"),
        ("Can't connect to RDP", "rdp_connection"),
        ("Disk space full", "disk_storage"),
    ]
    
    passed = 0
    for query, expected_category in test_cases:
        category, confidence = rag.classify_query(query)
        status = "PASS" if category == expected_category else "FAIL"
        print(f"{status}: '{query}' -> {category} (expected: {expected_category})")
        if status == "PASS":
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)

def test_retrieval(rag):
    """Test retrieval quality"""
    print("\n" + "="*70)
    print("TEST 4: Retrieval Quality")
    print("="*70)
    
    query = "How do I reset my password?"
    results = rag.retrieve_context_advanced(query, category="password_reset")
    
    print(f"Query: {query}")
    print(f"Retrieved: {len(results)} results")
    
    if len(results) > 0:
        print(f"Top result score: {results[0].get('combined_score', 0):.3f}")
        print(f"Top result category: {results[0]['metadata'].get('category')}")
        print("PASS: Retrieval working")
        return True
    else:
        print("FAIL: No results retrieved")
        return False

def test_expert_responses(rag):
    """Test expert response generation"""
    print("\n" + "="*70)
    print("TEST 5: Expert Response Generation")
    print("="*70)
    
    test_queries = [
        "How do I reset my password?",
        "QuickBooks error -6177",
        "Can't connect to Remote Desktop"
    ]
    
    passed = 0
    for query in test_queries:
        print(f"\nQuery: {query}")
        start = time.time()
        
        try:
            result = rag.process_query_expert(query)
            elapsed = time.time() - start
            
            print(f"Category: {result['category']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Time: {elapsed:.2f}s")
            print(f"Response length: {len(result['response'])} chars")
            print(f"Sources: {len(result.get('sources', []))}")
            
            # Check response quality
            response = result['response']
            has_content = len(response) > 50
            has_sources = len(result.get('sources', [])) > 0
            not_escalated = not result.get('escalate', False)
            
            if has_content and has_sources and not_escalated:
                print("PASS: Good response")
                passed += 1
            else:
                print("FAIL: Poor response quality")
                
        except Exception as e:
            print(f"FAIL: {e}")
    
    print(f"\nPassed: {passed}/{len(test_queries)}")
    return passed == len(test_queries)

def test_api_compatibility():
    """Test API compatibility"""
    print("\n" + "="*70)
    print("TEST 6: API Compatibility")
    print("="*70)
    
    try:
        # Try importing the API
        from src.simple_api import app, rag_engine, EXPERT_MODE
        
        print(f"API Mode: {'EXPERT' if EXPERT_MODE else 'REGULAR'}")
        print(f"RAG Engine Type: {type(rag_engine).__name__}")
        
        if EXPERT_MODE:
            print("PASS: API using Expert RAG")
            return True
        else:
            print("WARN: API using Regular RAG (Expert RAG import failed)")
            return False
            
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("EXPERT RAG PRE-DEPLOYMENT TEST SUITE")
    print("="*70)
    
    results = []
    
    # Test 1: Vector Store
    results.append(("Vector Store", test_vector_store()))
    
    # Test 2: Expert RAG Init
    success, rag = test_expert_rag_init()
    results.append(("Expert RAG Init", success))
    
    if not success:
        print("\nCannot continue tests without Expert RAG")
        return False
    
    # Test 3: Query Classification
    results.append(("Query Classification", test_query_classification(rag)))
    
    # Test 4: Retrieval
    results.append(("Retrieval Quality", test_retrieval(rag)))
    
    # Test 5: Expert Responses
    results.append(("Expert Responses", test_expert_responses(rag)))
    
    # Test 6: API Compatibility
    results.append(("API Compatibility", test_api_compatibility()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "="*70)
        print("ALL TESTS PASSED! Ready to deploy to Render.")
        print("="*70)
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Upgrade to Expert RAG system'")
        print("3. git push origin main")
        return True
    else:
        print("\n" + "="*70)
        print("SOME TESTS FAILED! Fix issues before deploying.")
        print("="*70)
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
