"""
Test Responses for User Review
Shows actual responses to common ticket queries
"""

from dotenv import load_dotenv
load_dotenv(override=True)

from src.rag_engine import RAGEngine
import time

# Initialize RAG engine
print("Initializing RAG engine...")
rag = RAGEngine()

print("\n" + "="*80)
print("TESTING CHATBOT RESPONSES - REAL TICKET SCENARIOS")
print("="*80)

# Real-world ticket queries
test_cases = [
    {
        "id": 1,
        "query": "I forgot my password, how do I reset it?",
        "category": "Password/Login"
    },
    {
        "id": 2,
        "query": "I'm getting QuickBooks error -6177 when trying to open my company file",
        "category": "QuickBooks Error"
    },
    {
        "id": 3,
        "query": "I can't connect to the Remote Desktop server. It says connection failed.",
        "category": "RDP Connection"
    },
    {
        "id": 4,
        "query": "The server is running very slow today. Everything is taking forever to load.",
        "category": "Server Performance"
    },
    {
        "id": 5,
        "query": "My Outlook keeps asking for my password over and over again",
        "category": "Email Issue"
    },
    {
        "id": 6,
        "query": "How do I add a new user to our server?",
        "category": "User Management"
    },
    {
        "id": 7,
        "query": "QuickBooks says 'You have exceeded the maximum number of users'",
        "category": "QuickBooks License"
    },
    {
        "id": 8,
        "query": "My printer is not showing up when I connect to the server",
        "category": "Printer Issue"
    }
]

results = []

for test in test_cases:
    print(f"\n{'='*80}")
    print(f"TEST {test['id']}: {test['category']}")
    print(f"{'='*80}")
    print(f"\n❓ USER QUERY:")
    print(f"   {test['query']}")
    
    # Get response
    start_time = time.time()
    result = rag.process_query(test['query'])
    response_time = time.time() - start_time
    
    # Display results
    print(f"\n📊 METADATA:")
    print(f"   Escalate: {result['escalate']}")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Sources Found: {len(result.get('sources', []))}")
    print(f"   Response Time: {response_time:.2f}s")
    print(f"   Tokens Used: {result.get('tokens_used', 'N/A')}")
    
    if result.get('sources'):
        print(f"\n📚 TOP SOURCES:")
        for i, source in enumerate(result['sources'][:3], 1):
            category = source.get('category', 'N/A')
            relevance = source.get('relevance')
            if relevance:
                print(f"   {i}. {category} (relevance: {relevance:.3f})")
            else:
                print(f"   {i}. {category}")
    
    print(f"\n💬 RESPONSE:")
    print(f"   {'-'*76}")
    # Wrap text for better readability
    response_text = result['response']
    words = response_text.split()
    line = "   "
    for word in words:
        if len(line) + len(word) + 1 > 80:
            print(line)
            line = "   " + word
        else:
            line += " " + word if line != "   " else word
    if line.strip():
        print(line)
    print(f"   {'-'*76}")
    
    # Store for summary
    results.append({
        "test_id": test['id'],
        "category": test['category'],
        "query": test['query'],
        "escalate": result['escalate'],
        "confidence": result['confidence'],
        "sources": len(result.get('sources', [])),
        "response_length": len(result['response']),
        "response_time": response_time,
        "has_support_number": "1-855-223-4887" in result['response'] or "855-223-4887" in result['response'],
        "mentions_kb_content": any(keyword in result['response'].lower() for keyword in ['quickbooks', 'server', 'rdp', 'remote', 'outlook', 'error', 'step'])
    })
    
    print(f"\n{'='*80}")
    time.sleep(1)  # Brief pause between tests

# Summary
print(f"\n\n{'='*80}")
print("SUMMARY OF ALL TESTS")
print("="*80)

total_tests = len(results)
escalated = sum(1 for r in results if r['escalate'])
high_confidence = sum(1 for r in results if r['confidence'] == 'high')
has_sources = sum(1 for r in results if r['sources'] >= 3)
has_support_num = sum(1 for r in results if r['has_support_number'])
mentions_kb = sum(1 for r in results if r['mentions_kb_content'])
avg_response_time = sum(r['response_time'] for r in results) / total_tests
avg_response_length = sum(r['response_length'] for r in results) / total_tests

print(f"\n📊 STATISTICS:")
print(f"   Total Tests: {total_tests}")
print(f"   Escalated: {escalated} ({escalated/total_tests*100:.1f}%)")
print(f"   High Confidence: {high_confidence} ({high_confidence/total_tests*100:.1f}%)")
print(f"   Has 3+ Sources: {has_sources} ({has_sources/total_tests*100:.1f}%)")
print(f"   Includes Support Number: {has_support_num} ({has_support_num/total_tests*100:.1f}%)")
print(f"   Mentions KB Content: {mentions_kb} ({mentions_kb/total_tests*100:.1f}%)")
print(f"   Avg Response Time: {avg_response_time:.2f}s")
print(f"   Avg Response Length: {avg_response_length:.0f} chars")

print(f"\n✅ QUALITY INDICATORS:")
if escalated == 0:
    print(f"   ✅ No unnecessary escalations")
else:
    print(f"   ⚠️  {escalated} queries escalated")

if high_confidence >= total_tests * 0.8:
    print(f"   ✅ High confidence rate: {high_confidence/total_tests*100:.0f}%")
else:
    print(f"   ⚠️  Low confidence rate: {high_confidence/total_tests*100:.0f}%")

if has_sources >= total_tests * 0.8:
    print(f"   ✅ Good source retrieval: {has_sources/total_tests*100:.0f}%")
else:
    print(f"   ⚠️  Poor source retrieval: {has_sources/total_tests*100:.0f}%")

if mentions_kb >= total_tests * 0.8:
    print(f"   ✅ Using KB content: {mentions_kb/total_tests*100:.0f}%")
else:
    print(f"   ⚠️  Not using KB content: {mentions_kb/total_tests*100:.0f}%")

print(f"\n{'='*80}")
print("REVIEW COMPLETE - Please review the responses above")
print("="*80)
print("\nLook for:")
print("  1. Are responses specific and helpful?")
print("  2. Do they reference KB procedures?")
print("  3. Do they include support contact info?")
print("  4. Are they better than generic AI responses?")
print("\nProvide feedback on what needs improvement!")
