"""Verify KB Updates"""
from src.vector_store import VectorStore

vs = VectorStore()
vs.create_collection()

# Test password reset
print("\n" + "="*70)
print("TEST 1: Password Reset (SelfCare Portal)")
print("="*70)
results = vs.search("SelfCare portal password reset", top_k=2)
for r in results:
    if "selfcare" in r['content'].lower():
        print("✓ SelfCare content found")
        print(f"  Preview: {r['content'][:150]}...")
        break

# Test disk storage
print("\n" + "="*70)
print("TEST 2: Disk Storage (Cleanup + Pricing)")
print("="*70)
results = vs.search("disk space full storage upgrade", top_k=2)
for r in results:
    content_lower = r['content'].lower()
    if "cleanup" in content_lower or "temp" in content_lower:
        print("✓ Cleanup steps found")
        print(f"  Preview: {r['content'][:150]}...")
    if "$" in r['content'] and ("40" in r['content'] or "60" in r['content']):
        print("✓ Pricing found")
        print(f"  Preview: {r['content'][:150]}...")
        break

print("\n" + "="*70)
print("Verification complete!")
print("="*70)
