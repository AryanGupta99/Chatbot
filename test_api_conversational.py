"""
Test the API with conversational approach
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_chat(message, conversation_id="test_conv"):
    """Test chat endpoint"""
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": message,
            "conversation_id": conversation_id
        }
    )
    return response.json()

def test_salesiq_webhook(message, session_id="test_session"):
    """Test SalesIQ webhook"""
    response = requests.post(
        f"{BASE_URL}/webhook/salesiq",
        json={
            "session_id": session_id,
            "message": {"text": message}
        }
    )
    return response.json()

print("="*70)
print("TESTING API CONVERSATIONAL APPROACH")
print("="*70)
print("\nMake sure the API is running: python src/simple_api.py")
print("="*70)

# Test 1: Greeting
print("\n\nTest 1: Initial Greeting")
print("-"*70)
try:
    result = test_chat("Hello")
    print(f"User: Hello")
    print(f"Bot: {result['response']}")
    print(f"✓ Expected: 'Hello! I'm AceBuddy. How can I assist you today?'")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Password reset conversation
print("\n\nTest 2: Password Reset Conversation")
print("-"*70)
conv_id = "pwd_test"
try:
    # First message
    result = test_chat("I need to reset my password", conv_id)
    print(f"User: I need to reset my password")
    print(f"Bot: {result['response']}")
    print(f"✓ Should ask if registered on SelfCare")
    
    # Follow-up
    result = test_chat("Yes, I'm registered", conv_id)
    print(f"\nUser: Yes, I'm registered")
    print(f"Bot: {result['response']}")
    print(f"✓ Should provide detailed steps")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Disk full conversation
print("\n\nTest 3: Disk Full Conversation")
print("-"*70)
conv_id = "disk_test"
try:
    # First message
    result = test_chat("My disk is full", conv_id)
    print(f"User: My disk is full")
    print(f"Bot: {result['response']}")
    print(f"✓ Should ask to check current space")
    
    # Follow-up
    result = test_chat("I have 2GB left", conv_id)
    print(f"\nUser: I have 2GB left")
    print(f"Bot: {result['response']}")
    print(f"✓ Should provide cleanup steps and upgrade options")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: SalesIQ webhook format
print("\n\nTest 4: SalesIQ Webhook Format")
print("-"*70)
try:
    result = test_salesiq_webhook("Hello")
    print(f"User: Hello")
    print(f"Bot: {result['replies'][0]}")
    print(f"✓ Should be simple greeting")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: SalesIQ password reset
print("\n\nTest 5: SalesIQ Password Reset")
print("-"*70)
session = "salesiq_pwd"
try:
    result = test_salesiq_webhook("I forgot my password", session)
    print(f"User: I forgot my password")
    print(f"Bot: {result['replies'][0]}")
    print(f"✓ Should ask clarifying question")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n\n" + "="*70)
print("TESTS COMPLETE")
print("="*70)
print("\nKey improvements:")
print("1. Simple greeting: 'Hello! I'm AceBuddy. How can I assist you today?'")
print("2. Asks clarifying questions first (2-3 sentences)")
print("3. Provides detailed solutions after understanding context")
print("4. No information dumping on first contact")
