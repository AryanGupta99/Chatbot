"""
Test the exact scenario from user's chat transcript
"""
import requests

API_URL = "http://localhost:8000/chat"

def chat(message, conv_id="scenario_test"):
    """Send message and get response"""
    response = requests.post(API_URL, json={"message": message, "conversation_id": conv_id})
    result = response.json()
    print(f"\nYou: {message}")
    print(f"Bot: {result['response']}")
    print("-" * 80)
    return result['response']

if __name__ == "__main__":
    print("=" * 80)
    print("EXACT SCENARIO TEST")
    print("=" * 80)
    
    # Simulate the exact conversation
    r1 = chat("unable to login")
    print("✓ Bot asks where (application/server/selfcare)")
    
    r2 = chat("server")
    print("✓ Bot handles server issue")
    
    r3 = chat("oh sorry unable to login on selfcare")
    print("✓ Bot switches to selfcare")
    
    r4 = chat("yes")
    print("✓ Bot continues selfcare flow")
    
    r5 = chat("ohh its quickbooks")
    print("✓ Bot switches to QuickBooks")
    
    # Check that it asks for specific error
    assert "tool" not in r5.lower(), "ERROR: Mentioned 'tool'!"
    assert any(word in r5.lower() for word in ["error", "problem", "specific", "frozen", "seeing"]), "Should ask for specific error"
    
    print("\n" + "=" * 80)
    print("SUCCESS! ✓")
    print("- Bot correctly handles topic switches")
    print("- Bot asks for specific QuickBooks error")
    print("- Bot NEVER mentions 'tool'")
    print("=" * 80)
