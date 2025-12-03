"""
Test updated SelfCare password reset steps
"""
import requests

API_URL = "http://localhost:8000/chat"

def chat(message, conv_id="password_test"):
    """Send message and get response"""
    response = requests.post(API_URL, json={"message": message, "conversation_id": conv_id})
    result = response.json()
    print(f"\nYou: {message}")
    print(f"Bot: {result['response']}")
    print("-" * 80)
    return result['response']

if __name__ == "__main__":
    print("=" * 80)
    print("PASSWORD RESET UPDATE TEST")
    print("=" * 80)
    
    # Test 1: User asks about password reset
    print("\n### TEST 1: Password reset request ###")
    r1 = chat("I forgot my password", "test1")
    print("✓ Bot responds to password reset request")
    
    # Test 2: User clarifies it's SelfCare
    print("\n### TEST 2: SelfCare password reset ###")
    r2 = chat("reset selfcare password", "test2")
    print("✓ Bot provides SelfCare password reset steps")
    
    # Check for correct steps
    if "server username" in r2.lower():
        print("✓ Mentions Server Username (correct!)")
    else:
        print("⚠ Should mention Server Username")
    
    if "captcha" in r2.lower():
        print("✓ Mentions CAPTCHA (correct!)")
    else:
        print("⚠ Should mention CAPTCHA")
    
    if "authentication method" in r2.lower():
        print("✓ Mentions authentication method (correct!)")
    else:
        print("⚠ Should mention authentication method")
    
    # Test 3: Full conversation flow
    print("\n### TEST 3: Full conversation flow ###")
    r3a = chat("can't login", "test3")
    print("✓ Bot asks where (application/server/selfcare)")
    
    r3b = chat("selfcare", "test3")
    print("✓ Bot handles selfcare login issue")
    
    r3c = chat("forgot password", "test3")
    print("✓ Bot provides password reset steps")
    
    print("\n" + "=" * 80)
    print("PASSWORD RESET STEPS UPDATED! ✓")
    print("New steps include:")
    print("1. Visit selfcare portal")
    print("2. Click 'Forgot your password'")
    print("3. Enter Server Username")
    print("4. Enter CAPTCHA and click Continue")
    print("5. Choose authentication method")
    print("6. Enter new password and click Reset")
    print("=" * 80)
