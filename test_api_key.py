"""Test if OpenAI API key works"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

print("="*60)
print("TESTING OPENAI API KEY")
print("="*60)
print(f"\nAPI Key found: {api_key[:20]}...{api_key[-10:]}")
print(f"API Key length: {len(api_key)}")

try:
    client = OpenAI(api_key=api_key)
    
    # Test with a simple embedding
    print("\nTesting API connection...")
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="test"
    )
    
    print("✅ API KEY WORKS!")
    print(f"   Embedding dimension: {len(response.data[0].embedding)}")
    print("\nYou can now run the vector store creation!")
    
except Exception as e:
    print(f"❌ API KEY ERROR: {e}")
    print("\nPlease check:")
    print("1. Your API key is correct")
    print("2. Your API key is active (not expired)")
    print("3. You have credits in your OpenAI account")
    print("\nGet a new key at: https://platform.openai.com/api-keys")
