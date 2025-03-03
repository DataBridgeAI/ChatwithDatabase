import os

def load_api_key():
    """Load API key from environment variables."""
    api_key = os.getenv("OPEN_AI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "OPEN API Key is missing. Please configure it in your .env file."
        )
    
    return api_key
