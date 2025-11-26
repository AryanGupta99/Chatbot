"""
Interactive testing script for AceBuddy chatbot
"""

from src.rag_engine import RAGEngine
from datetime import datetime

def test_interactive():
    print("="*60)
    print("ACEBUDDY CHATBOT - INTERACTIVE TEST")
    print("="*60)
    print("\nInitializing RAG engine...")
    
    try:
        rag = RAGEngine()
        print("✅ RAG engine ready!\n")
    except Exception as e:
        print(f"❌ Error initializing RAG engine: {e}")
        print("Make sure you've run: python run_pipeline.py")
        return
    
    print("Type your questions (or 'quit' to exit)")
    print("-" * 60)
    
    session_history = []
    
    while True:
        try:
            query = input("\n🧑 You: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            # Process query
            print("🤖 AceBuddy: ", end="", flush=True)
            result = rag.process_query(query, session_history)
            
            print(result['response'])
            
            # Show metadata
            print(f"\n   📊 Confidence: {result['confidence']}")
            if result['escalate']:
                print("   ⚠️  Escalating to human agent")
            if result.get('sources'):
                print(f"   📚 Sources: {len(result['sources'])}")
                for source in result['sources'][:2]:
                    print(f"      - {source['category']}: {source['id']}")
            
            # Update history
            session_history.append({"role": "user", "content": query})
            session_history.append({"role": "assistant", "content": result['response']})
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def test_predefined():
    """Test with predefined queries"""
    print("="*60)
    print("ACEBUDDY CHATBOT - PREDEFINED TEST CASES")
    print("="*60)
    
    try:
        rag = RAGEngine()
        print("✅ RAG engine ready!\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    test_cases = [
        {
            "query": "I forgot my password, how do I reset it?",
            "expected_category": "User Management"
        },
        {
            "query": "My QuickBooks is showing error -6177, what should I do?",
            "expected_category": "QuickBooks"
        },
        {
            "query": "I can't connect to Remote Desktop, it says server not found",
            "expected_category": "Remote Desktop"
        },
        {
            "query": "How much does 200GB storage upgrade cost?",
            "expected_category": "Server"
        },
        {
            "query": "My Outlook keeps asking for password",
            "expected_category": "Email"
        },
        {
            "query": "I need to add a new user to the system",
            "expected_category": "User Management"
        },
        {
            "query": "The server is running very slow",
            "expected_category": "Server"
        },
        {
            "query": "I need urgent help with billing issue",
            "expected_category": "Escalation"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}/{len(test_cases)}]")
        print(f"Query: {test['query']}")
        print("-" * 60)
        
        result = rag.process_query(test['query'])
        
        print(f"Response: {result['response'][:200]}...")
        print(f"\nConfidence: {result['confidence']}")
        print(f"Escalate: {result['escalate']}")
        
        if result.get('sources'):
            print(f"Sources ({len(result['sources'])}):")
            for source in result['sources'][:2]:
                print(f"  - {source['category']}: {source['id']}")
        
        results.append({
            "query": test['query'],
            "expected": test['expected_category'],
            "confidence": result['confidence'],
            "escalate": result['escalate'],
            "sources": len(result.get('sources', []))
        })
        
        print()
    
    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    high_confidence = sum(1 for r in results if r['confidence'] == 'high')
    escalated = sum(1 for r in results if r['escalate'])
    
    print(f"Total tests: {len(results)}")
    print(f"High confidence: {high_confidence}/{len(results)} ({high_confidence/len(results)*100:.0f}%)")
    print(f"Escalated: {escalated}/{len(results)} ({escalated/len(results)*100:.0f}%)")
    print(f"Avg sources per query: {sum(r['sources'] for r in results)/len(results):.1f}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        test_predefined()
    else:
        test_interactive()
