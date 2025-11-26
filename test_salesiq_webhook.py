"""Test SalesIQ Webhook Locally"""

import requests
import json

# Change this to your deployed URL or use localhost for local testing
BASE_URL = "http://localhost:8000"
# For deployed version: BASE_URL = "https://your-app.onrender.com"

def test_webhook_accessibility():
    """Test if webhook endpoint is accessible"""
    print("\n=== Test 1: Webhook Accessibility ===")
    try:
        response = requests.get(f"{BASE_URL}/webhook/salesiq/test")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Webhook endpoint is accessible")
            return True
        else:
            print("❌ Webhook endpoint returned error")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_webhook_with_message():
    """Test webhook with a sample message"""
    print("\n=== Test 2: Webhook with Sample Message ===")
    
    payload = {
        "chat_id": "test_chat_123",
        "visitor_id": "visitor_456",
        "message": "I need help with password reset",
        "visitor_name": "Test User",
        "visitor_email": "test@example.com"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/salesiq",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("✅ Webhook processed message successfully")
                return True
            else:
                print(f"⚠️ Webhook returned error: {result.get('error')}")
                return False
        else:
            print("❌ Webhook returned HTTP error")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_health_endpoint():
    """Test API health endpoint"""
    print("\n=== Test 3: API Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print("❌ API health check failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_root_endpoint():
    """Test API root endpoint"""
    print("\n=== Test 4: API Root Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ API root is accessible")
            return True
        else:
            print("❌ API root returned error")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("SalesIQ Webhook Testing")
    print("=" * 60)
    print(f"\nTesting against: {BASE_URL}")
    print("\nMake sure your API server is running!")
    print("Run: python -m uvicorn src.enhanced_api:app --host 0.0.0.0 --port 8000")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Root Endpoint", test_root_endpoint()))
    results.append(("Health Check", test_health_endpoint()))
    results.append(("Webhook Accessibility", test_webhook_accessibility()))
    results.append(("Webhook Message Processing", test_webhook_with_message()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Your webhook is ready for SalesIQ.")
        print("\nNext steps:")
        print("1. Deploy to Render (if not already deployed)")
        print("2. Configure webhook URL in SalesIQ: https://your-app.onrender.com/webhook/salesiq")
        print("3. Test from SalesIQ dashboard")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("- Ensure API server is running")
        print("- Check .env file has OPENAI_API_KEY set")
        print("- Verify all dependencies are installed")
        print("- Check SALESIQ_WEBHOOK_TROUBLESHOOTING.md for more help")

if __name__ == "__main__":
    main()
