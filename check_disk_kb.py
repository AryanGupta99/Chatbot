from src.vector_store import VectorStore

vs = VectorStore()
vs.create_collection()

print("Searching for disk storage pricing...")
results = vs.search("200GB 120 month storage upgrade pricing", top_k=5)

for i, r in enumerate(results, 1):
    print(f"\n{i}. Doc: {r['metadata'].get('doc_id', 'unknown')}")
    print(f"   Content: {r['content'][:300]}")
    if "$120" in r['content'] or "200GB" in r['content']:
        print("   ✓ FOUND PRICING!")
