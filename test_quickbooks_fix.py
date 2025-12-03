"""
Test QuickBooks handling - should ask for specifics, not mention "tool"
"""
import requests
import json

API_URL = "http://localhost:8000/chat"

def test_chat(message, conversation_id="test_qb"):
    """Send test message"""
    response = requests.post(
        API_URL,
        json={
            "message": message,
            "conversation_id": conversation_id
        }
    )
    result = response.json()
    print(f"\nUser: {message}")
    print(f"Bot: {result['response']}")
    print("-" * 80)
    return result['response']

if __name__ == "__main__":
    print("=" * 80)
    print("TESTING QUICKBOOKS HANDLING")
    print("=" * 80)
    
    # Test 1: Vague "unable to login"
    print("\n### TEST 1: Vague login issue ###")
    response1 = test_chat("unable to login", "test1")
    assert "tool" not in response1.lower(), "Should NOT mention 'tool'"
    assert any(word in response1.lower() for word in ["application", "server", "selfcare"]), "Should ask about issue type"
    print("✓ Correctly asks for clarification")
    
    # Test 2: User clarifies it's QuickBooks
    print("\n### TEST 2: User says QuickBooks ###")
    response2 = test_chat("quickbooks", "test1")
    assert "tool" not in response2.lower(), "Should NOT mention 'tool'"
    assert any(word in response2.lower() for word in ["error", "problem", "specific", "frozen", "issue"]), "Should ask for specific error"
    print("✓ Asks for specific QuickBooks error")
    
    # Test 3: Direct QuickBooks issue
    print("\n### TEST 3: Direct QuickBooks issue ###")
    response3 = test_chat("quickbooks not working", "test2")
    assert "tool" not in response3.lower(), "Should NOT mention 'tool'"
    assert any(word in response3.lower() for word in ["error", "problem", "specific", "seeing"]), "Should ask what's wrong"
    print("✓ Asks for details, doesn't mention tool")
    
    # Test 4: QuickBooks frozen - should ask server type
    print("\n### TEST 4: QuickBooks frozen ###")
    response4 = test_chat("quickbooks frozen", "test3")
    assert "tool" not in response4.lower(), "Should NOT mention 'tool'"
    print("✓ Handles frozen QuickBooks correctly")
    
    # Test 5: Server issue
    print("\n### TEST 5: Server issue ###")
    response5 = test_chat("server", "test1")
    assert "tool" not in response5.lower(), "Should NOT mention 'tool'"
    print("✓ Handles server issue")
    
    # Test 6: SelfCare issue
    print("\n### TEST 6: SelfCare issue ###")
    response6 = test_chat("selfcare", "test1")
    assert "tool" not in response6.lower(), "Should NOT mention 'tool'"
    print("✓ Handles SelfCare issue")
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED! ✓")
    print("- No 'tool' mentions")
    print("- Asks for specific errors")
    print("- Categorizes as application/server/selfcare")
    print("=" * 80)
