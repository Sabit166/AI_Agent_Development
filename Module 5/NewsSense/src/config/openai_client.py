import os
import logfire
from dotenv import load_dotenv
from openai import AsyncOpenAI
from .settings import BASE_URL, API_KEY, MODEL_NAME
from agents import OpenAIChatCompletionsModel

# Configure logfire but avoid the problematic agents instrumentation
logfire.configure()
# logfire.instrument_openai_agents()  # Comment this out to avoid conflicts
logfire.instrument_openai()  # This should work fine

# Initialize the shared OpenAI client
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)

def get_openai_model():
    """Get configured OpenAI model instance"""
    return {
        "client": client,
        "model": MODEL_NAME
    }
    
def get_chat_completion_model():
    return OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client)


# Export commonly used components
__all__ = ['client', 'get_openai_model', 'MODEL_NAME']