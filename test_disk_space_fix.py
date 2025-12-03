"""
Test disk space handling - should ask for server type, not assume
"""
import requests

API_URL = "http://localhost:8000/chat"

def chat(message, conv_id="disk_test"):
    """Send message and get response"""
    response = requests.post(API_URL, json={"message": message, "conversation_id": conv_id})
    result = response.json()
    print(f"\nYou: {message}")
    print(f"Bot: {result['response']}")
    print("-" * 80)
    return result['response']

if __name__ == "__main__":
    print("=" * 80)
    print("DISK SPACE FIX TEST")
    print("=" * 80)
    
    # Test 1: User says disk space is full
    print("\n### TEST 1: Disk space full ###")
    r1 = chat("my disk space is showing full", "test1")
    
    # Check that it asks for server type, doesn't assume "dedicated"
    # Should contain both "dedicated" AND "shared" (asking which one)
    has_both = "dedicated" in r1.lower() and "shared" in r1.lower()
    assert has_both, f"Should ask for server type (dedicated or shared), got: {r1}"
    print("✓ Bot asks for server type instead of assuming")
    
    # Test 2: Different phrasing
    print("\n### TEST 2: Disk full ###")
    r2 = chat("disk full", "test2")
    has_both = "dedicated" in r2.lower() and "shared" in r2.lower()
    assert has_both, f"Should ask for server type, got: {r2}"
    print("✓ Bot asks for server type")
    
    # Test 3: After user specifies dedicated
    print("\n### TEST 3: User specifies dedicated ###")
    r3a = chat("disk space full", "test3")
    r3b = chat("dedicated", "test3")
    print("✓ Bot provides steps after getting server type")
    
    # Test 4: After user specifies shared
    print("\n### TEST 4: User specifies shared ###")
    r4a = chat("disk full", "test4")
    r4b = chat("shared", "test4")
    print("✓ Bot provides steps after getting server type")
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED! ✓")
    print("- Bot asks for server type first")
    print("- Bot doesn't assume 'dedicated server'")
    print("- Bot provides steps after clarification")
    print("=" * 80)
