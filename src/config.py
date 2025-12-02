"""Simple config for Render deployment"""
import os
from pathlib import Path

class Settings:
    # OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Generation params
    temperature = float(os.getenv("TEMPERATURE", "0.4"))
    max_tokens = int(os.getenv("MAX_TOKENS", "900"))
    
    # RAG params
    top_k_results = 5
    similarity_threshold = 0.3
    max_context_length = 3000
    
    # ChromaDB
    chroma_persist_directory = str(Path(__file__).parent.parent / "data" / "chroma")
    collection_name = "acebuddy_kb"

settings = Settings()
