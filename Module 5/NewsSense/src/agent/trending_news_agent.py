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
from models.output_format import TrendingNewsOutput
from config.openai_client import get_chat_completion_model
from tools.news_fetcher import get_trending_news

trending_news_agent = Agent[UserContext](
    name="Trending News Specialist",
    handoff_description="Specialist agent for fetching and organizing trending news by category.",
    instructions="""
    You are a trending news specialist. Your job is to fetch the latest trending news headlines
    from various categories and present them in an organized, easy-to-read format.
    
    You can:
    - Fetch trending headlines from multiple news categories
    - Organize news by topic and importance
    - Provide source information and timestamps
    - Filter news based on user preferences
    
    Always provide current, accurate, and well-organized news information.
    """,
    model=get_chat_completion_model(),
    tools=[get_trending_news],
    output_type=TrendingNewsOutput
)

async def main():
    print("📰 Testing Trending News Agent...")
    print("=" * 60)
    
    user_context = UserContext()
    
    test_queries = [
        "Get me the latest trending news",
        "What's happening in technology news?",
        "Show me business headlines from today",
        "What are the top stories right now?",
        "Get trending news in science and general categories"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📈 Query {i}: {query}")
        print("-" * 50)
        
        try:
            # Run the agent with the query
            response = await Runner.run(trending_news_agent, query, context=user_context)
            print(f"📰 Response:")

            if hasattr(response.final_output, 'headlines'):
                for j, headline in enumerate(response.final_output.headlines[:5], 1):
                    print(f"  {j}. {headline.title}")
                    print(f"     Source: {headline.source} | Category: {headline.category}")
            else:
                print(f"  {response}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 50)
    
    print("\n✅ Trending News Agent testing completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())