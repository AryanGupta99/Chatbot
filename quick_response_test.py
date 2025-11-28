"""Quick Response Test - Show 3 key examples"""

from dotenv import load_dotenv
load_dotenv(override=True)

from src.rag_engine import RAGEngine

print("Initializing...")
rag = RAGEngine()

print("\n" + "="*80)
print("QUICK RESPONSE TEST - 3 EXAMPLES")
print("="*80)

tests = [
    "I forgot my password, how do I reset it?",
    "QuickBooks error -6177 when opening company file",
    "Can't connect to Remote Desktop server"
]

for i, query in enumerate(tests, 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}: {query}")
    print("="*80)
    
    result = rag.process_query(query)
    
    print(f"\n📊 Escalate: {result['escalate']} | Confidence: {result['confidence']} | Sources: {len(result.get('sources', []))}")
    
    print(f"\n💬 RESPONSE:")
    print(result['response'])
    
    print(f"\n✅ QUALITY CHECK:")
    has_support = "1-855-223-4887" in result['response'] or "855" in result['response']
    has_steps = any(x in result['response'].lower() for x in ['step', '1.', '2.', 'follow'])
    has_kb_terms = any(x in result['response'].lower() for x in ['quickbooks', 'server', 'remote', 'password', 'error'])
    
    print(f"   Support number mentioned: {'✅' if has_support else '❌'}")
    print(f"   Includes steps/procedures: {'✅' if has_steps else '❌'}")
    print(f"   Uses KB terminology: {'✅' if has_kb_terms else '❌'}")
    print(f"   Response length: {len(result['response'])} chars")

print(f"\n{'='*80}")
print("DONE - Please review the 3 responses above")
print("="*80)
