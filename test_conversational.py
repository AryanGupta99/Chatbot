"""
Test conversational approach - should ask clarifying questions first
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EXPERT_PROMPT = """You are AceBuddy, an expert IT support assistant for ACE Cloud Hosting.

CONVERSATIONAL APPROACH:
- FIRST RESPONSE: Ask 1-2 clarifying questions to understand the situation better
- FOLLOW-UP: Provide detailed solution only after understanding the context
- Be friendly and conversational, not robotic
- Keep initial responses short (2-3 sentences max)

EXAMPLES:
User: "I need to reset my password"
You: "I can help with that! Are you currently registered on our SelfCare portal at https://selfcare.acecloudhosting.com?"

User: "My disk is full"
You: "Let me help you with that. First, can you check how much space you currently have? Right-click on your C: drive and select Properties to see the available space."

User: "QuickBooks error"
You: "I can assist with QuickBooks issues. What's the specific error code or message you're seeing?"

User: "Can't connect to RDP"
You: "I'll help you troubleshoot this. Are you connecting from Windows or Mac? And what error message are you seeing?"

CRITICAL KNOWLEDGE BASE:

**PASSWORD RESET:**
- SelfCare Portal: https://selfcare.acecloudhosting.com
- Steps: 1) Go to portal 2) Click "Forgot Password" 3) Enter email 4) Check email for reset link (2-3 min)
- If not enrolled: Contact support@acecloudhosting.com or call helpdesk
- Requires Google Authenticator enrollment

**DISK STORAGE:**
- Check space: Right-click C: drive → Properties
- Quick cleanup: Delete temp files (%temp%), run Disk Cleanup utility
- Upgrade tiers: 40GB ($10/mo), 80GB ($20/mo), 120GB ($30/mo), 200GB ($50/mo)
- Ticket ETA: 2-4 hours for upgrade
- Contact: support@acecloudhosting.com

RESPONSE STYLE:
- INITIAL CONTACT: Ask clarifying questions (1-2 sentences)
- AFTER CLARIFICATION: Provide detailed steps (100-150 words max)
- Use numbered steps for solutions
- Include specific URLs and contact info
- Be conversational and friendly

GREETING:
When user first says hello/hi or starts conversation, respond with:
"Hello! I'm AceBuddy. How can I assist you today?"
"""

def test_conversation(user_message, conversation_history=None):
    """Test a conversational exchange"""
    if conversation_history is None:
        conversation_history = []
    
    messages = [{"role": "system", "content": EXPERT_PROMPT}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=500
    )
    
    ai_response = response.choices[0].message.content.strip()
    return ai_response

# Test scenarios
print("="*70)
print("TESTING CONVERSATIONAL APPROACH")
print("="*70)

# Test 1: Greeting
print("\n\n" + "="*70)
print("Test 1: Initial Greeting")
print("="*70)
print("User: Hello")
response = test_conversation("Hello")
print(f"Bot: {response}")

# Test 2: Password reset - should ask clarifying question
print("\n\n" + "="*70)
print("Test 2: Password Reset (Initial)")
print("="*70)
print("User: I need to reset my password")
conversation = []
response = test_conversation("I need to reset my password", conversation)
print(f"Bot: {response}")
conversation.append({"role": "user", "content": "I need to reset my password"})
conversation.append({"role": "assistant", "content": response})

# Follow-up
print("\n" + "-"*70)
print("User: Yes, I'm registered")
response = test_conversation("Yes, I'm registered", conversation)
print(f"Bot: {response}")

# Test 3: Disk full - should ask clarifying question
print("\n\n" + "="*70)
print("Test 3: Disk Full (Initial)")
print("="*70)
print("User: My disk is full")
conversation = []
response = test_conversation("My disk is full", conversation)
print(f"Bot: {response}")
conversation.append({"role": "user", "content": "My disk is full"})
conversation.append({"role": "assistant", "content": response})

# Follow-up
print("\n" + "-"*70)
print("User: I have only 2GB left")
response = test_conversation("I have only 2GB left", conversation)
print(f"Bot: {response}")

# Test 4: QuickBooks error - should ask for error code
print("\n\n" + "="*70)
print("Test 4: QuickBooks Error (Initial)")
print("="*70)
print("User: QuickBooks is not working")
conversation = []
response = test_conversation("QuickBooks is not working", conversation)
print(f"Bot: {response}")
conversation.append({"role": "user", "content": "QuickBooks is not working"})
conversation.append({"role": "assistant", "content": response})

# Follow-up
print("\n" + "-"*70)
print("User: Error -6177")
response = test_conversation("Error -6177", conversation)
print(f"Bot: {response}")

# Test 5: RDP connection - should ask for details
print("\n\n" + "="*70)
print("Test 5: RDP Connection (Initial)")
print("="*70)
print("User: Can't connect to remote desktop")
conversation = []
response = test_conversation("Can't connect to remote desktop", conversation)
print(f"Bot: {response}")
conversation.append({"role": "user", "content": "Can't connect to remote desktop"})
conversation.append({"role": "assistant", "content": response})

# Follow-up
print("\n" + "-"*70)
print("User: I'm on Mac and getting connection failed error")
response = test_conversation("I'm on Mac and getting connection failed error", conversation)
print(f"Bot: {response}")

print("\n\n" + "="*70)
print("TESTS COMPLETE")
print("="*70)
print("\nExpected behavior:")
print("- Greeting should be simple: 'Hello! I'm AceBuddy. How can I assist you today?'")
print("- Initial responses should ask clarifying questions (2-3 sentences)")
print("- Follow-up responses should provide detailed solutions")
print("- No information dumping on first contact")
