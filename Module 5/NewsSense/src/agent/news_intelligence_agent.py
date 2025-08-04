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

# FIXED: Correct import paths
from agent.trending_news_agent import trending_news_agent
from agent.news_summerizer_agent import news_summarizer_agent
from agent.fact_checker_agent import fact_checker_agent
from agent.conversational_agent import conversational_agent

# Rest of your imports
from agents import Agent, Runner
from models.user_context import UserContext
from models.output_format import NewsIntelligenceOutput
from config.openai_client import get_chat_completion_model

# Your agent definition remains the same
news_intelligence_agent = Agent[UserContext](
    name="News Intelligence Specialist",
    instructions="""
    You are a news intelligence specialist who helps users to track, verify and summarize news from across the web.
    
    You can detect trending topics, fact check claims using web search and retrieve and provide concise, readable news briefs.
    
    You can:
    1. Pull headlines across categories and group them by topic.
    2. Verify claims using RAG and summarize sources to support or refute claims.
    3. Summarize lengthy contents into 3-5 bullet points and use extractive or abstractive summarization techniques.
    
    You can also use the general conversation agent to carry out normal conversations with the user.
    If the user asks a question that is not related to news intelligence, you can handoff to the general conversation agent.
    If the user asks a question that is related to news intelligence, you can use the appropriate agent to handle the request.
    If you are not sure which agent to use, you can ask the user for clarification.
    If you are not sure how to answer a question, you can ask the user for more information.
    you yourself don't try to answer questions. Always handover to other agents or if user query is not clear, ask for clarification.

    Always be frank and honest about news.
    """,
    model=get_chat_completion_model(),
    handoffs=[trending_news_agent, fact_checker_agent, news_summarizer_agent, conversational_agent],
    output_type=NewsIntelligenceOutput
)

async def main():
    print("🤖 Testing News Intelligence Agent...")
    print("=" * 60)
    
    user_context = UserContext()
    
    test_queries = [
        "What are the latest trending news stories?",
        "Can you fact-check this claim: Artificial intelligence will replace all human jobs by 2030",
        "Summarize the latest technology news for me",
        "What's happening in business news today?",
        "Hello, how are you doing today?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 50)
        
        try:
            # Run the agent with the query
            response = await Runner.run(news_intelligence_agent, query, context=user_context)
            print(f"🤖 Response: {response}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 50)
    
    print("\n✅ News Intelligence Agent testing completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())