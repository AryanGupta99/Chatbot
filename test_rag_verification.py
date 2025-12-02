"""
Quick test to verify RAG is actually being used
"""
import requests
import json

API_URL = "https://chatbot-68y4.onrender.com"

def test_rag_response():
    """Test with a specific KB question"""
    
    # Test 1: Ask about disk storage (should have specific pricing)
    print("=" * 60)
    print("TEST 1: Disk Storage Question")
    print("=" * 60)
    
    response = requests.post(
        f"{API_URL}/chat",
        json={
            "message": "What are the disk storage upgrade options?",
            "conversation_id": "test_rag_verify"
        }
    )
    
    result = response.json()
    answer = result["response"]
    
    print(f"Question: What are the disk storage upgrade options?")
    print(f"\nResponse:\n{answer}\n")
    
    # Check if response contains specific KB info
    has_pricing = any(price in answer for price in ["$10", "$20", "$30", "$50"])
    has_tiers = any(tier in answer for tier in ["40GB", "80GB", "120GB", "200GB"])
    
    print("✅ RAG VERIFICATION:")
    print(f"  - Contains pricing info: {'YES ✅' if has_pricing else 'NO ❌'}")
    print(f"  - Contains tier details: {'YES ✅' if has_tiers else 'NO ❌'}")
    
    if has_pricing and has_tiers:
        print("\n🎉 RAG IS WORKING! Response contains specific KB data!")
    else:
        print("\n⚠️ RAG might not be working - generic response")
    
    print("\n" + "=" * 60)
    print("TEST 2: Password Reset Question")
    print("=" * 60)
    
    response2 = requests.post(
        f"{API_URL}/chat",
        json={
            "message": "How do I reset my password?",
            "conversation_id": "test_rag_verify2"
        }
    )
    
    result2 = response2.json()
    answer2 = result2["response"]
    
    print(f"Question: How do I reset my password?")
    print(f"\nResponse:\n{answer2}\n")
    
    # Check for SelfCare portal mention
    has_selfcare = "selfcare.acecloudhosting.com" in answer2.lower()
    has_phone = "1-888-415-5240" in answer2
    
    print("✅ RAG VERIFICATION:")
    print(f"  - Mentions SelfCare portal: {'YES ✅' if has_selfcare else 'NO ❌'}")
    print(f"  - Contains support phone: {'YES ✅' if has_phone else 'NO ❌'}")
    
    if has_selfcare or has_phone:
        print("\n🎉 RAG IS WORKING! Response contains specific KB data!")
    else:
        print("\n⚠️ RAG might not be working - generic response")

if __name__ == "__main__":
    test_rag_response()
