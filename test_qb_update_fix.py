"""
Test QuickBooks update issue - should NOT mention Tool Hub
"""
import requests

API_URL = "http://localhost:8000/chat"

def chat(message, conv_id="qb_update_test"):
    """Send message and get response"""
    response = requests.post(API_URL, json={"message": message, "conversation_id": conv_id})
    result = response.json()
    print(f"\nYou: {message}")
    print(f"Bot: {result['response']}")
    print("-" * 80)
    return result['response']

if __name__ == "__main__":
    print("=" * 80)
    print("QUICKBOOKS UPDATE FIX TEST")
    print("=" * 80)
    
    # Test the exact scenario from user
    print("\n### EXACT USER SCENARIO ###")
    r1 = chat("can you help me with quickbooks issue", "test1")
    print("✓ Bot asks for specific error")
    
    r2 = chat("it is giving me application required update", "test1")
    print("✓ Bot responds to update issue")
    
    # Check it does NOT mention Tool Hub
    if "tool hub" in r2.lower():
        print("❌ ERROR: Bot mentioned Tool Hub (should NOT for updates!)")
        print(f"Response: {r2}")
        exit(1)
    else:
        print("✓ Bot does NOT mention Tool Hub (correct!)")
    
    # Check it mentions the correct solution
    if "help" in r2.lower() and "update" in r2.lower():
        print("✓ Bot mentions Help → Update (correct!)")
    
    r3 = chat("yes closed", "test1")
    print("✓ Bot continues with next step")
    
    # Continue to see full flow
    r4 = chat("opened", "test1")
    print("✓ Bot provides next step")
    
    if "tool hub" in r4.lower():
        print("❌ ERROR: Bot mentioned Tool Hub in step 2")
        exit(1)
    
    print("\n" + "=" * 80)
    print("SUCCESS! ✓")
    print("- Bot does NOT mention Tool Hub for updates")
    print("- Bot uses Help → Update QuickBooks Desktop")
    print("- Tool Hub is only for specific errors (not general updates)")
    print("=" * 80)
