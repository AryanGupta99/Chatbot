"""Test if API key is loaded correctly"""
import os
from dotenv import load_dotenv

# Force reload .env
load_dotenv(override=True)

api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key from env: {api_key[:20]}..." if api_key else "No API key found")

# Also test config
from config import settings
print(f"API Key from config: {settings.openai_api_key[:20]}..." if settings.openai_api_key else "No API key in config")
