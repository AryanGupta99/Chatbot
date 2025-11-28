"""Test Render API Directly"""
import requests
import json

# Your Render URL
RENDER_URL = "https://acebuddy-api.onrender.com"  # Update with your actual URL

def test_disk_query():
    """Test disk space query"""
    
    payload = {
        "message": "My disk is full, can you help?",
        "chat_id": "test_123",
        "visitor_id": "test_visitor",
        "visitor_email": "test@example.com",
        "visitor_name": "Test User"
    }
    
    print("Testing Render API...")
    print(f"URL: {RENDER_URL}/chat")
    print(f"Query: {payload['message']}\n")
    
    try:
        response = requests.post(
            f"{RENDER_URL}/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response:")
            print("-" * 70)
            print(result.get('response', 'No response'))
            print("-" * 70)
            
            # Check for key elements
            response_text = result.get('response', '').lower()
            if 'temp' in response_text or 'cleanup' in response_text:
                print("\n✓ Contains cleanup steps")
            if '$' in result.get('response', ''):
                print("✓ Contains pricing")
            if any(price in result.get('response', '') for price in ['$28', '$40', '$60', '$120']):
                print("✓ Contains specific pricing tiers")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_disk_query()
