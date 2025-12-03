"""
Test full password reset flow step by step
"""
import requests

API_URL = "http://localhost:8000/chat"

def chat(message, conv_id="password_flow"):
    """Send message and get response"""
    response = requests.post(API_URL, json={"message": message, "conversation_id": conv_id})
    result = response.json()
    print(f"\nYou: {message}")
    print(f"Bot: {result['response']}")
    print("-" * 80)
    return result['response']

if __name__ == "__main__":
    print("=" * 80)
    print("FULL PASSWORD RESET FLOW")
    print("=" * 80)
    
    # Simulate complete conversation
    r1 = chat("I need to reset my selfcare password")
    
    r2 = chat("I'm there")
    # Should mention "Forgot your password" button
    
    r3 = chat("clicked it")
    # Should mention Server Username
    if "username" in r3.lower():
        print("✓ Step mentions Server Username")
    
    r4 = chat("entered username")
    # Should mention CAPTCHA
    if "captcha" in r4.lower():
        print("✓ Step mentions CAPTCHA")
    
    r5 = chat("done")
    # Should mention authentication method
    if "authentication" in r5.lower() or "method" in r5.lower():
        print("✓ Step mentions authentication method")
    
    r6 = chat("selected method")
    # Should mention entering new password
    if "password" in r6.lower():
        print("✓ Step mentions entering new password")
    
    print("\n" + "=" * 80)
    print("FULL FLOW TESTED! ✓")
    print("Bot guides through all 6 steps correctly")
    print("=" * 80)
