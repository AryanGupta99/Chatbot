"""Test SalesIQ webhook with correct format"""

import requests
import json

# Change this to your deployed URL or use localhost for local testing
BASE_URL = "http://localhost:8000"
# For deployed: BASE_URL = "https://acebuddy-api.onrender.com"

def test_webhook_format():
    """Test webhook returns correct SalesIQ format"""
    
    print("=" * 60)
    print("Testing SalesIQ Webhook Format")
    print("=" * 60)
    
    # Test 1: Simple greeting
    print("\n[Test 1] Simple greeting")
    payload1 = {
        "session_id": "visitor-123",
        "message": "Hello",
        "visitor": {
            "id": "v-1",
            "name": "Alice",
            "email": "alice@example.com"
        }
    }
    
    response1 = requests.post(f"{BASE_URL}/webhook/salesiq", json=payload1)
    print(f"Status: {response1.status_code}")
    print(f"Response: {json.dumps(response1.json(), indent=2)}")
    
    # Validate format
    data1 = response1.json()
    assert "action" in data1, "Missing 'action' field"
    assert "replies" in data1, "Missing 'replies' field"
    assert "session_id" in data1, "Missing 'session_id' field"
    assert isinstance(data1["replies"], list), "'replies' must be a list"
    assert len(data1["replies"]) > 0, "'replies' must not be empty"
    print("✅ Format is correct!")
    
    # Test 2: Password reset
    print("\n[Test 2] Password reset request")
    payload2 = {
        "session_id": "visitor-456",
        "message": "How do I reset my password?",
        "visitor": {
            "id": "v-2",
            "name": "Bob",
            "email": "bob@example.com"
        }
    }
    
    response2 = requests.post(f"{BASE_URL}/webhook/salesiq", json=payload2)
    print(f"Status: {response2.status_code}")
    print(f"Response: {json.dumps(response2.json(), indent=2)}")
    
    # Validate format
    data2 = response2.json()
    assert "action" in data2, "Missing 'action' field"
    assert "replies" in data2, "Missing 'replies' field"
    assert "session_id" in data2, "Missing 'session_id' field"
    assert data2["session_id"] == "visitor-456", "session_id mismatch"
    print("✅ Format is correct!")
    
    # Test 3: Empty message
    print("\n[Test 3] Empty message")
    payload3 = {
        "session_id": "visitor-789",
        "message": "",
        "visitor": {
            "id": "v-3",
            "name": "Charlie"
        }
    }
    
    response3 = requests.post(f"{BASE_URL}/webhook/salesiq", json=payload3)
    print(f"Status: {response3.status_code}")
    print(f"Response: {json.dumps(response3.json(), indent=2)}")
    
    # Validate format
    data3 = response3.json()
    assert "action" in data3, "Missing 'action' field"
    assert "replies" in data3, "Missing 'replies' field"
    print("✅ Format is correct!")
    
    # Test 4: Conversation with history
    print("\n[Test 4] Follow-up message (conversation history)")
    payload4 = {
        "session_id": "visitor-456",  # Same session as test 2
        "message": "I forgot my username",
        "visitor": {
            "id": "v-2",
            "name": "Bob"
        }
    }
    
    response4 = requests.post(f"{BASE_URL}/webhook/salesiq", json=payload4)
    print(f"Status: {response4.status_code}")
    print(f"Response: {json.dumps(response4.json(), indent=2)}")
    
    # Validate format
    data4 = response4.json()
    assert "action" in data4, "Missing 'action' field"
    assert "replies" in data4, "Missing 'replies' field"
    print("✅ Format is correct!")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nExpected SalesIQ format:")
    print(json.dumps({
        "action": "reply",
        "replies": ["Response text here"],
        "session_id": "visitor-123"
    }, indent=2))
    print("\n✅ Your webhook is returning the correct format for SalesIQ!")

if __name__ == "__main__":
    try:
        test_webhook_format()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server")
        print(f"Make sure server is running at {BASE_URL}")
        print("\nTo start server locally:")
        print("  python src/simple_api.py")
    except AssertionError as e:
        print(f"❌ Format validation failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
