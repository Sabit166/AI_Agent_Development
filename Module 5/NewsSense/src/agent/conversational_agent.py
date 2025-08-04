import sys
import os

# Fix the import path FIRST
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)

# Add both src and project root to Python path
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents import Agent, Runner
from models.user_context import UserContext
from models.output_format import ConversationOutput
from config.openai_client import get_chat_completion_model

conversational_agent = Agent[UserContext](
    name="General Conversation Specialist",
    handoff_description="Specialist agent for giving basic responses to the user to carry out a normal conversation as opposed to structured output.",
    instructions="""
    You are a helpful news intelligence assistant who can engage in natural conversation.
    
    Your capabilities include:
    - Answering questions about news and current events
    - Providing guidance on using the news intelligence system
    - Engaging in friendly, informative conversations
    - Suggesting relevant news-related actions
    
    Always be helpful, clear, and steer conversations toward news-related topics when appropriate.
    Maintain a professional yet friendly tone.
    """,
    model=get_chat_completion_model(),
    output_type=ConversationOutput,
    tools=[]
)

async def main():
    print("💬 Testing Conversational Agent...")
    print("=" * 60)
    
    user_context = UserContext()
    
    test_queries = [
        "Hello! How can you help me with news?",
        "What's the weather like today?",
        "Can you explain how fact-checking works?",
        "I'm interested in technology news. What can you do for me?",
        "Thank you for your help!",
        "What are the main features of this news intelligence system?",
        "How reliable are your news sources?",
        "Can you help me understand bias in news reporting?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n💬 Query {i}: {query}")
        print("-" * 50)
        
        try:
            # Run the agent with the query
            response = await Runner.run(conversational_agent, query, context=user_context)
            print(f"🤖 Response:")
            
            if hasattr(response.final_output, 'message'):
                print(f"  {response.final_output.message}")
                if hasattr(response.final_output, 'suggestions') and response.final_output.suggestions:
                    print(f"  Suggestions: {', '.join(response.final_output.suggestions)}")
            else:
                print(f"  {response.final_output}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 50)
    
    print("\n✅ Conversational Agent testing completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())