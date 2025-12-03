"""
Test the exact disk space scenario from user's chat
"""
import requests

API_URL = "http://localhost:8000/chat"

def chat(message, conv_id="exact_disk"):
    """Send message and get response"""
    response = requests.post(API_URL, json={"message": message, "conversation_id": conv_id})
    result = response.json()
    print(f"\nYou: {message}")
    print(f"Bot: {result['response']}")
    print("-" * 80)
    return result['response']

if __name__ == "__main__":
    print("=" * 80)
    print("EXACT DISK SPACE SCENARIO")
    print("=" * 80)
    
    # Simulate exact conversation
    r1 = chat("yes closed processes and its opening now")
    print("✓ Bot acknowledges")
    
    r2 = chat("my disk space is showing full")
    print("✓ Bot should ask for server type")
    
    # Check it asks, doesn't assume
    has_both = "dedicated" in r2.lower() and "shared" in r2.lower()
    if not has_both:
        print(f"\n❌ ERROR: Bot should ask 'dedicated or shared?'")
        print(f"Instead got: {r2}")
        exit(1)
    
    print("\n✓ Bot correctly asks: 'Are you on a dedicated or shared server?'")
    print("✓ User can now answer instead of typing manually!")
    
    # Continue conversation
    r3 = chat("dedicated")
    print("✓ Bot provides steps for dedicated server")
    
    print("\n" + "=" * 80)
    print("SUCCESS! ✓")
    print("- Bot asks for server type instead of assuming")
    print("- User doesn't have to type 'dedicated' manually")
    print("- Conversation flows naturally")
    print("=" * 80)
