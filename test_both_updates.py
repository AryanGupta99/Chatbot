"""Test Both Updates - Password Reset & Disk Storage"""
from src.rag_engine import RAGEngine

rag = RAGEngine()

tests = [
    {
        "name": "Password Reset - SelfCare Portal",
        "query": "I forgot my password",
        "expected": ["selfcare", "google authenticator", "acecloudhosting.com"]
    },
    {
        "name": "Disk Storage - Cleanup First",
        "query": "My C drive is showing red",
        "expected": ["temp", "cleanup", "delete"]
    },
    {
        "name": "Storage Upgrade - Pricing",
        "query": "How much does storage upgrade cost?",
        "expected": ["$120", "200gb", "$60"]
    }
]

print("="*70)
print("TESTING KNOWLEDGE BASE UPDATES")
print("="*70)

for i, test in enumerate(tests, 1):
    print(f"\n[TEST {i}] {test['name']}")
    print("-"*70)
    
    result = rag.process_query(test['query'])
    response = result['response'].lower()
    
    found = []
    for keyword in test['expected']:
        if keyword.lower() in response:
            found.append(keyword)
    
    if found:
        print(f"✓ PASS - Found: {', '.join(found)}")
    else:
        print(f"✗ FAIL - Expected keywords not found")
    
    print(f"\nResponse preview: {result['response'][:300]}...")

print("\n" + "="*70)
print("TESTING COMPLETE")
print("="*70)
