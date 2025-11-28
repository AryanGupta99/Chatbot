"""Quick Check"""
from src.vector_store import VectorStore

vs = VectorStore()
vs.create_collection()

print("\n1. Checking SelfCare Portal content...")
r = vs.search("SelfCare portal Google Authenticator", top_k=1)
if r and "google authenticator" in r[0]['content'].lower():
    print("   ✓ SelfCare guide is in KB")
else:
    print("   ✗ SelfCare guide NOT found")

print("\n2. Checking Disk Storage cleanup...")
r = vs.search("disk cleanup temp files", top_k=1)
if r and ("temp" in r[0]['content'].lower() or "cleanup" in r[0]['content'].lower()):
    print("   ✓ Cleanup steps are in KB")
else:
    print("   ✗ Cleanup steps NOT found")

print("\n3. Checking Storage Pricing...")
r = vs.search("200GB 120 month storage", top_k=1)
if r and "$120" in r[0]['content']:
    print("   ✓ Pricing is in KB")
    print(f"   Preview: {r[0]['content'][:200]}")
else:
    print("   ✗ Pricing NOT found")

print("\n✓ All checks complete!")
