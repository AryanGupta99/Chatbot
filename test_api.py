"""Test the Enhanced API endpoints"""

import requests
import json
from datetime import datetime

def test_api_endpoints():
    base_url = "http://localhost:8000"
    
    print("="*60)
    print("TESTING ENHANCED API ENDPOINTS")
    print("="*60)
    
    # Test 1: Health check
    print("\n[Test 1] Health Check")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"   Service: {data['service']}")
            print(f"   Version: {data['version']}")
            print(f"   Features: {data['features']}")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Detailed health
    print("\n[Test 2] Detailed Health Check")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"   RAG Documents: {data['rag_engine']['total_documents']}")
            print(f"   Zobot Q&A Pairs: {data['zobot_qa_pairs']}")
            print(f"   Conversation Flows: {data['conversation_flows']}")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Chat endpoint - Greeting
    print("\n[Test 3] Chat - Greeting")
    print("-" * 30)
    try:
        payload = {
            "query": "Hello there!",
            "session_id": "test_session_1"
        }
        response = requests.post(f"{base_url}/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Source: {data['source']}")
            print(f"   Confidence: {data['confidence']}")
            print(f"   Escalate: {data['escalate']}")
            print(f"   Quick Actions: {len(data['quick_actions'])}")
            print(f"   Response: {data['response'][:100]}...")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Chat endpoint - Password Reset
    print("\n[Test 4] Chat - Password Reset")
    print("-" * 30)
    try:
        payload = {
            "query": "I forgot my password",
            "session_id": "test_session_2"
        }
        response = requests.post(f"{base_url}/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Source: {data['source']}")
            print(f"   Confidence: {data['confidence']}")
            print(f"   Escalate: {data['escalate']}")
            print(f"   Quick Actions: {[a['text'] for a in data['quick_actions'][:3]]}")
            print(f"   Response: {data['response'][:150]}...")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Chat endpoint - QuickBooks (Hybrid)
    print("\n[Test 5] Chat - QuickBooks Error (Hybrid)")
    print("-" * 30)
    try:
        payload = {
            "query": "QuickBooks error -6177",
            "session_id": "test_session_3"
        }
        response = requests.post(f"{base_url}/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Source: {data['source']}")
            print(f"   Confidence: {data['confidence']}")
            print(f"   Escalate: {data['escalate']}")
            print(f"   RAG Sources: {len(data['sources'])}")
            print(f"   Quick Actions: {[a['text'] for a in data['quick_actions'][:3]]}")
            print(f"   Response Length: {len(data['response'])} chars")
            if data.get('follow_up'):
                print(f"   Follow-up: {data['follow_up'][:100]}...")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Quick Action
    print("\n[Test 6] Quick Action - Password Reset")
    print("-" * 30)
    try:
        payload = {
            "action": "password_reset",
            "session_id": "test_session_4"
        }
        response = requests.post(f"{base_url}/action", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Source: {data['source']}")
            print(f"   Confidence: {data['confidence']}")
            print(f"   Escalate: {data['escalate']}")
            print(f"   Response: {data['response'][:100]}...")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 7: Get flows
    print("\n[Test 7] Get Conversation Flows")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/flows")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available Flows: {data['flows']}")
            print(f"   Total Q&A Pairs: {data['total_qa_pairs']}")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 8: Get stats
    print("\n[Test 8] Get Statistics")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Active Sessions: {data['active_sessions']}")
            print(f"   RAG Documents: {data['rag_engine']['total_documents']}")
            print(f"   Zobot Q&A Pairs: {data['zobot_integration']['qa_pairs']}")
            print(f"   Conversation Flows: {data['zobot_integration']['conversation_flows']}")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 9: Chat with conversation history
    print("\n[Test 9] Chat - Conversation History")
    print("-" * 30)
    try:
        session_id = "test_session_history"
        
        # First message
        payload = {
            "query": "I have a QuickBooks problem",
            "session_id": session_id
        }
        response = requests.post(f"{base_url}/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ First Message - Source: {data['source']}")
        
        # Follow-up message
        payload = {
            "query": "It's error -6177",
            "session_id": session_id
        }
        response = requests.post(f"{base_url}/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Follow-up - Source: {data['source']}")
            print(f"   Response Length: {len(data['response'])} chars")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 10: Escalation flow
    print("\n[Test 10] Chat - Escalation (Billing)")
    print("-" * 30)
    try:
        payload = {
            "query": "What's your pricing for storage?",
            "session_id": "test_session_escalate"
        }
        response = requests.post(f"{base_url}/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Source: {data['source']}")
            print(f"   Escalate: {data['escalate']}")
            print(f"   Confidence: {data['confidence']}")
            print(f"   Response: {data['response'][:150]}...")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("API TESTING COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_api_endpoints()
