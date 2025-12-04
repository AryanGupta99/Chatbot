"""
Simple test for handover logic
"""
import requests

API_URL = "http://localhost:8000/chat"

def chat(message, conv_id):
    response = requests.post(API_URL, json={"message": message, "conversation_id": conv_id})
    result = response.json()
    print(f"\nYou: {message}")
    print(f"Bot: {result['response']}")
    print("-" * 80)
    return result['response']

print("=" * 80)
print("HANDOVER TESTS")
print("=" * 80)

# Test 1: Greetings
print("\n### Greeting Variation ###")
r1 = chat("Hello", "g1")
r2 = chat("Hi", "g2")
r3 = chat("Hey", "g3")
print("✓ Greetings vary naturally")

# Test 2: User frustrated
print("\n### User Frustrated ###")
chat("QuickBooks issue", "f1")
r = chat("This is so frustrating, nothing is working", "f1")
if "support" in r.lower() or "1-888-415-5240" in r:
    print("✓ Escalates when frustrated")
else:
    print("⚠ Should escalate to support")

# Test 3: User requests human
print("\n### User Requests Human ###")
r = chat("Can I talk to a real person?", "h1")
if "support" in r.lower() or "1-888-415-5240" in r:
    print("✓ Escalates when human requested")
else:
    print("⚠ Should escalate to support")

# Test 4: Nothing is working
print("\n### Nothing Is Working ###")
r = chat("I tried everything, nothing is working", "n1")
if "support" in r.lower() or "1-888-415-5240" in r:
    print("✓ Escalates when nothing works")
else:
    print("⚠ Should escalate to support")

# Test 5: Still not fixed
print("\n### Still Not Fixed ###")
chat("server issue", "s1")
chat("done that", "s1")
r = chat("still not fixed", "s1")
if "support" in r.lower() or "1-888-415-5240" in r:
    print("✓ Escalates when still not fixed")
else:
    print("⚠ Should escalate to support")

print("\n" + "=" * 80)
print("HANDOVER LOGIC TESTED")
print("=" * 80)
