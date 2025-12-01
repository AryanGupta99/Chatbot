"""
Test that chatbot provides correct contact information
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Use the same prompt as the API
EXPERT_PROMPT = open('src/simple_api_working.py', 'r').read().split('EXPERT_PROMPT = """')[1].split('"""')[0]

def test_query(message):
    """Test a query"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": EXPERT_PROMPT},
            {"role": "user", "content": message}
        ],
        temperature=0.3,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

print("="*70)
print("TESTING CONTACT INFORMATION")
print("="*70)

test_cases = [
    "What's your phone number?",
    "How do I contact support?",
    "Give me the support number",
    "I need to call someone",
    "What's the contact number?",
    "How can I reach support team?",
    "I want to speak to someone"
]

for query in test_cases:
    print(f"\n{'='*70}")
    print(f"User: {query}")
    print("="*70)
    response = test_query(query)
    print(f"Bot: {response}")
    
    # Check if phone number is in response
    if "1-888-415-5240" in response:
        print("✅ Phone number included")
    else:
        print("❌ Phone number MISSING")
    
    # Check if email is in response
    if "support@acecloudhosting.com" in response:
        print("✅ Email included")
    else:
        print("⚠️ Email not included")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\nExpected: All responses should include phone number 1-888-415-5240")
