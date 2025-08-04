import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
LOGFIRE_TOKEN = os.getenv("LOGFIRE_TOKEN")


# Validation
if not BASE_URL or not API_KEY or not MODEL_NAME:
    raise ValueError("Please set BASE_URL, API_KEY, and MODEL_NAME in your .env file.")

if not LOGFIRE_TOKEN:
    print("⚠️  Warning: LOGFIRE_TOKEN not set. Logging will be limited.")

# Model Configuration
DEFAULT_MODEL_SETTINGS = {
    "temperature": 0.1,
    "max_tokens": 1000,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}

# News Configuration
NEWS_FEEDS = {
    "general": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "business": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZ4ZERBU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
    "technology": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
    "science": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en"
}

# Fact-checking Configuration
FACT_CHECK_SITES = ['snopes', 'politifact', 'factcheck', 'reuters', 'ap.org', 'bbc']
SEARCH_TIMEOUT = 10
MAX_CONTENT_LENGTH = 1000