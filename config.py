import os
from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = "your_openai_api_key_here"
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    
    # Vector DB
    chroma_persist_directory: str = "./data/chroma"
    collection_name: str = "acebuddy_kb"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_secret_key: str = "change-this-secret-key-in-production"
    
    # Zoho
    zoho_webhook_secret: Optional[str] = None
    zoho_api_endpoint: Optional[str] = None
    
    # RAG
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 10
    similarity_threshold: float = 0.3
    max_context_length: int = 4000
    
    # Response
    temperature: float = 0.3
    max_tokens: int = 800
    fallback_to_agent_threshold: float = 0.2
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
