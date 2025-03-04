# import os
# from dotenv import load_dotenv

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# load_dotenv(os.path.join(BASE_DIR, "config", ".env"))  # Adjust the path to the .env file

# def load_api_key():
#     """Load API key from environment variables."""
#     api_key = os.getenv("OPENAI_API_KEY")
    
#     if not api_key:
#         raise ValueError(
#             "OPEN API Key is missing. Please configure it in your .env file."
#         )
    
#     return api_key


import os
from dotenv import load_dotenv

load_dotenv()

def load_api_key():
    """Load API key from environment variables"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Google API Key is missing. Please configure it in your .env file.")
    return api_key

# # Call the function to check if it loads the API key correctly
# try:
#     api_key = load_api_key()
#     print("API key loaded successfully:", api_key)
# except ValueError as e:
#     #print(e)
#     print(print("Current working directory:", os.getcwd()))