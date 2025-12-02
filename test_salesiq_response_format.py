"""
Test SalesIQ webhook response format
"""
import requests
import json

API_URL = "https://chatbot-68y4.onrender.com/webhook/salesiq"

def test_salesiq_format():
    """Test the exact format SalesIQ receives"""
    
    # Simulate SalesIQ webhook payload
    payload = {
        "session_id": "test_session_123",
        "message": {
            "text": "How to resolve server slowness issue?"
        }
    }
    
    print("=" * 60)
    print("Testing SalesIQ Webhook Response Format")
    print("=" * 60)
    print(f"\nSending payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            verify=False  # Skip SSL verification for testing
        )
        
        print(f"\n✅ Status Code: {response.status_code}")
        print(f"\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\nResponse Body:")
        response_data = response.json()
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        # Validate format
        print("\n" + "=" * 60)
        print("VALIDATION:")
        print("=" * 60)
        
        checks = {
            "Has 'action' field": "action" in response_data,
            "'action' is 'reply'": response_data.get("action") == "reply",
            "Has 'replies' field": "replies" in response_data,
            "'replies' is a list": isinstance(response_data.get("replies"), list),
            "Has at least 1 reply": len(response_data.get("replies", [])) > 0,
            "Reply is not empty": len(response_data.get("replies", [""])[0]) > 0,
            "Reply length < 1000": len(response_data.get("replies", [""])[0]) < 1000,
            "Has 'session_id'": "session_id" in response_data,
        }
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}")
        
        if all(checks.values()):
            print("\n🎉 ALL CHECKS PASSED! Format is correct for SalesIQ")
        else:
            print("\n⚠️ SOME CHECKS FAILED! SalesIQ might reject this format")
        
        # Show reply content
        if response_data.get("replies"):
            reply = response_data["replies"][0]
            print(f"\n📝 Reply Preview:")
            print(f"   Length: {len(reply)} characters")
            print(f"   Content: {reply[:200]}...")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_salesiq_format()
