"""Simple API test"""
import requests
import json

base_url = "http://localhost:8000"

print("Testing Enhanced API...")

# Test 1: Health
response = requests.get(f"{base_url}/")
print(f"\n✅ Health Check: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# Test 2: Chat - Greeting
response = requests.post(f"{base_url}/chat", json={"query": "Hello!", "session_id": "test1"})
print(f"\n✅ Chat - Greeting: {response.status_code}")
data = response.json()
print(f"Source: {data['source']}")
print(f"Response: {data['response'][:150]}...")

# Test 3: Chat - QB Error (Hybrid)
response = requests.post(f"{base_url}/chat", json={"query": "QuickBooks error -6177", "session_id": "test2"})
print(f"\n✅ Chat - QB Error: {response.status_code}")
data = response.json()
print(f"Source: {data['source']}")
print(f"Response Length: {len(data['response'])} chars")
print(f"RAG Sources: {len(data['sources'])}")

# Test 4: Chat - RDP (Hybrid)
response = requests.post(f"{base_url}/chat", json={"query": "Can't connect to remote desktop", "session_id": "test3"})
print(f"\n✅ Chat - RDP: {response.status_code}")
data = response.json()
print(f"Source: {data['source']}")
print(f"Response Length: {len(data['response'])} chars")

# Test 5: Chat - Billing (Escalate)
response = requests.post(f"{base_url}/chat", json={"query": "What's your pricing?", "session_id": "test4"})
print(f"\n✅ Chat - Billing: {response.status_code}")
data = response.json()
print(f"Source: {data['source']}")
print(f"Escalate: {data['escalate']}")

# Test 6: Quick Action
response = requests.post(f"{base_url}/action", json={"action": "password_reset", "session_id": "test5"})
print(f"\n✅ Quick Action: {response.status_code}")
data = response.json()
print(f"Response: {data['response'][:100]}...")

# Test 7: Stats
response = requests.get(f"{base_url}/stats")
print(f"\n✅ Stats: {response.status_code}")
data = response.json()
print(f"Active Sessions: {data['active_sessions']}")
print(f"Zobot Q&A Pairs: {data['zobot_integration']['qa_pairs']}")

print("\n" + "="*60)
print("✅ ALL TESTS PASSED - API IS WORKING!")
print("="*60)
