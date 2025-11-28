"""
Test Password Reset Knowledge Base
"""

from src.rag_engine import RAGEngine

def test_password_reset():
    """Test password reset queries"""
    
    print("="*70)
    print("TESTING PASSWORD RESET KNOWLEDGE")
    print("="*70)
    
    # Initialize RAG engine
    print("\n[1/3] Initializing RAG engine...")
    rag = RAGEngine()
    print("✅ RAG engine initialized")
    
    # Test queries
    test_queries = [
        "I forgot my password, how do I reset it?",
        "How do I change my server password?",
        "What is the SelfCare portal?",
        "How do I enroll in MFA?",
        "I need to reset my password but haven't enrolled"
    ]
    
    print(f"\n[2/3] Testing {len(test_queries)} password reset queries...")
    print("="*70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Query {i}: {query}")
        print(f"{'='*70}")
        
        try:
            result = rag.process_query(query)
            response = result['response']
            print(f"\n✅ Response:\n{response}")
            
            # Check if response mentions SelfCare
            if "selfcare" in response.lower() or "self care" in response.lower():
                print("\n✓ Response mentions SelfCare Portal")
            else:
                print("\n⚠️  Response does NOT mention SelfCare Portal")
            
            # Check if response mentions Google Authenticator
            if "google authenticator" in response.lower():
                print("✓ Response mentions Google Authenticator")
            
            # Check if response mentions the portal URL
            if "acecloudhosting.com" in response.lower():
                print("✓ Response includes portal URL")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    print(f"\n{'='*70}")
    print("[3/3] Testing complete!")
    print(f"{'='*70}")

if __name__ == "__main__":
    test_password_reset()
