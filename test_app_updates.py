"""
Test application update handling - should direct to support team
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
    print("APPLICATION UPDATE HANDLING TEST")
    print("=" * 80)
    
    applications = [
        "QuickBooks",
        "Lacerte",
        "Drake",
        "Pro Series",
        "CFS",
        "1099",
        "Adobe"
    ]
    
    for i, app in enumerate(applications):
        print(f"\n### TEST {i+1}: {app} Update ###")
        conv_id = f"test_{i}"
        
        r1 = chat(f"{app} says application requires update", conv_id)
        
        # Check it directs to support
        has_support = "support" in r1.lower() or "1-888-415-5240" in r1
        if not has_support:
            print(f"❌ ERROR: Should direct to support team!")
            print(f"Response: {r1}")
            exit(1)
        
        # Check it does NOT try to guide user through update
        bad_phrases = ["open", "go to help", "download", "tool hub", "click", "first"]
        if any(phrase in r1.lower() for phrase in bad_phrases):
            print(f"⚠ WARNING: Seems to be guiding user (should just direct to support)")
        
        print(f"✓ {app} update correctly directs to support team")
    
    # Test the exact user scenario
    print("\n### EXACT USER SCENARIO ###")
    r1 = chat("can you help me with quickbooks issue", "exact")
    r2 = chat("it is giving me application required update", "exact")
    
    if "support" in r2.lower() or "1-888-415-5240" in r2:
        print("✓ QuickBooks update directs to support")
    else:
        print("❌ ERROR: Should direct to support!")
        print(f"Response: {r2}")
        exit(1)
    
    if "tool hub" in r2.lower():
        print("❌ ERROR: Should NOT mention Tool Hub for updates!")
        exit(1)
    else:
        print("✓ Does NOT mention Tool Hub")
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED! ✓")
    print("- All application updates direct to support team")
    print("- No Tool Hub mentions for updates")
    print("- Support: 1-888-415-5240 or support@acecloudhosting.com")
    print("=" * 80)
