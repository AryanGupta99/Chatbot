"""
Test to find SalesIQ's actual character limit
"""
import requests
import json

API_URL = "https://chatbot-68y4.onrender.com/webhook/salesiq"

def test_different_lengths():
    """Test responses of different lengths"""
    
    test_cases = [
        ("Short", 500),
        ("Medium", 1000),
        ("Long", 1500),
        ("Very Long", 2000),
        ("Extremely Long", 2500),
        ("Massive", 3000),
    ]
    
    print("=" * 70)
    print("TESTING SALESIQ RESPONSE LENGTH LIMITS")
    print("=" * 70)
    
    for name, target_length in test_cases:
        # Create a message of specific length
        test_message = f"Test {name} response. " + ("A" * (target_length - 30))
        
        payload = {
            "session_id": f"test_{name.lower().replace(' ', '_')}",
            "message": {
                "text": "Tell me about server performance in detail"
            }
        }
        
        print(f"\n{name} Test ({target_length} chars):")
        print("-" * 70)
        
        try:
            response = requests.post(
                API_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get("replies", [""])[0]
                actual_length = len(reply)
                
                print(f"✅ Status: {response.status_code}")
                print(f"📏 Response Length: {actual_length} chars")
                print(f"📝 Preview: {reply[:100]}...")
                
                if actual_length < target_length:
                    print(f"⚠️ Response was truncated from {target_length} to {actual_length}")
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATION:")
    print("=" * 70)
    print("Based on the results above, the safe limit appears to be:")
    print("- If all tests pass: No hard limit (use 2000 chars)")
    print("- If some fail: Use the highest successful length")
    print("=" * 70)

if __name__ == "__main__":
    print("\n⚠️ NOTE: This test will send actual requests to your deployed API")
    print("Make sure your API is deployed and running on Render\n")
    
    input("Press Enter to continue...")
    test_different_lengths()
