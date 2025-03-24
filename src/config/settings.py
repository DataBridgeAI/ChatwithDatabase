import os
from dotenv import load_dotenv

load_dotenv()

def load_api_key():
    """Load API key from environment variables"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPEN AI API Key is missing. Please configure it in your .env file.")
    return api_key