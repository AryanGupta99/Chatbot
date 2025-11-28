"""Final Verification of Updates"""
from src.rag_engine import RAGEngine

rag = RAGEngine()

print("\n" + "="*70)
print("FINAL VERIFICATION - PASSWORD RESET & DISK STORAGE")
print("="*70)

# Test 1: Password Reset
print("\n[TEST 1] Password Reset with SelfCare Portal")
print("-"*70)
result = rag.process_query("How do I reset my password?")
response = result['response']
print(response[:500] + "...")

if "selfcare" in response.lower():
    print("\n✓ PASS: Mentions SelfCare Portal")
else:
    print("\n✗ FAIL: Does not mention SelfCare Portal")

# Test 2: Disk Storage with Cleanup
print("\n" + "="*70)
print("[TEST 2] Disk Storage - Cleanup Steps")
print("-"*70)
result = rag.process_query("My disk is full, what should I do?")
response = result['response']
print(response[:500] + "...")

if "temp" in response.lower() or "cleanup" in response.lower():
    print("\n✓ PASS: Mentions cleanup steps")
else:
    print("\n✗ FAIL: Does not mention cleanup steps")

# Test 3: Storage Pricing
print("\n" + "="*70)
print("[TEST 3] Storage Upgrade Pricing")
print("-"*70)
result = rag.process_query("How much does storage upgrade cost?")
response = result['response']
print(response[:500] + "...")

if "$120" in response or "$60" in response or "200GB" in response:
    print("\n✓ PASS: Includes pricing information")
else:
    print("\n✗ FAIL: Does not include pricing")

print("\n" + "="*70)
print("VERIFICATION COMPLETE")
print("="*70)
