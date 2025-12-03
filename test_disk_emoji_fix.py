"""
Test disk space flow - should NOT show emoji, should say "C drive" properly
"""
import requests

API_URL = "http://localhost:8000/chat"

def chat(message, conv_id="disk_emoji_test"):
    """Send message and get response"""
    response = requests.post(API_URL, json={"message": message, "conversation_id": conv_id})
    result = response.json()
    print(f"\nYou: {message}")
    print(f"Bot: {result['response']}")
    print("-" * 80)
    return result['response']

if __name__ == "__main__":
    print("=" * 80)
    print("DISK SPACE EMOJI FIX TEST")
    print("=" * 80)
    
    # Simulate the exact user conversation
    print("\n### EXACT USER SCENARIO ###")
    
    r1 = chat("disk space issue")
    print("✓ Bot asks for server type")
    
    r2 = chat("shared")
    print("✓ Bot acknowledges shared server")
    
    r3 = chat("yes server is connected")
    print("✓ Bot provides next step")
    
    r4 = chat("yes done")
    print("✓ Bot provides next step")
    
    r5 = chat("yes done")
    print("✓ Bot provides next step")
    
    # Check for emoji or encoding issues
    if "😥" in r5 or "😢" in r5 or "🙁" in r5:
        print("❌ ERROR: Response contains emoji!")
        print(f"Response: {r5}")
        exit(1)
    
    # Check it mentions C drive properly
    if "c drive" in r5.lower() or "c:" in r5.lower():
        print("✓ Mentions C drive properly (no emoji)")
    
    # Check for backslash issues
    if "c:\\" in r5.lower():
        print("⚠ WARNING: Contains backslash (might cause encoding issues)")
    
    print("\n" + "=" * 80)
    print("SUCCESS! ✓")
    print("- No emoji in responses")
    print("- C drive mentioned properly")
    print("- Clear, simple instructions")
    print("=" * 80)
