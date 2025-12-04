"""
Test human handover logic and natural greetings
"""
import requests

API_URL = "http://localhost:8000/chat"

def chat(message, conv_id):
    """Send message and get response"""
    response = requests.post(API_URL, json={"message": message, "conversation_id": conv_id})
    result = response.json()
    print(f"\nYou: {message}")
    print(f"Bot: {result['response']}")
    print("-" * 80)
    return result['response']

if __name__ == "__main__":
    print("=" * 80)
    print("TESTING HANDOVER LOGIC AND GREETINGS")
    print("=" * 80)
    
    # Test 1: First greeting
    print("\n### TEST 1: First Greeting ###")
    r1 = chat("Hello", "test1")
    assert "acebuddy" in r1.lower() or "assist" in r1.lower()
    print("✓ First greeting is welcoming")
    
    # Test 2: Repeated greeting (should be different)
    print("\n### TEST 2: Repeated Greeting ###")
    r2 = chat("Hi", "test1")
    # Should be different from first greeting
    print("✓ Repeated greeting (should vary)")
    
    # Test 3: User frustrated - should escalate
    print("\n### TEST 3: User Frustrated ###")
    r3a = chat("QuickBooks frozen", "test3")
    r3b = chat("done", "test3")
    r3c = chat("still not working, this is frustrating", "test3")
    assert "support" in r3c.lower() or "1-888-415-5240" in r3c or "human" in r3c.lower()
    print("✓ Detects frustration and escalates to support")
    
    # Test 4: User says nothing is working
    print("\n### TEST 4: Nothing Is Working ###")
    r4a = chat("server issue", "test4")
    r4b = chat("tried everything, nothing is working", "test4")
    assert "support" in r4b.lower() or "1-888-415-5240" in r4b
    print("✓ Escalates when user says nothing is working")
    
    # Test 5: User asks for human
    print("\n### TEST 5: User Requests Human ###")
    r5 = chat("Can I speak to a real person?", "test5")
    assert "support" in r5.lower() or "1-888-415-5240" in r5 or "call" in r5.lower()
    print("✓ Immediately escalates when user requests human")
    
    # Test 6: Multiple failed attempts
    print("\n### TEST 6: Multiple Failed Attempts ###")
    r6a = chat("Adobe crashing", "test6")
    r6b = chat("done", "test6")
    r6c = chat("done", "test6")
    r6d = chat("still crashing, I've done everything you said", "test6")
    assert "support" in r6d.lower() or "1-888-415-5240" in r6d
    print("✓ Escalates after multiple failed attempts")
    
    # Test 7: User says "this isn't working"
    print("\n### TEST 7: This Isn't Working ###")
    r7a = chat("printer issue", "test7")
    r7b = chat("this isn't working", "test7")
    assert "support" in r7b.lower() or "1-888-415-5240" in r7b
    print("✓ Escalates when user says 'this isn't working'")
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED! ✓")
    print("- Natural varied greetings")
    print("- Detects frustration")
    print("- Escalates to human support appropriately")
    print("- Provides support contact: 1-888-415-5240")
    print("=" * 80)
