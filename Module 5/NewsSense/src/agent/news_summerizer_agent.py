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
from models.output_format import NewsSummaryOutput
from config.openai_client import get_chat_completion_model
from tools.summarizer import get_news_summary

news_summarizer_agent = Agent[UserContext](
    name="News Summarization Specialist",
    handoff_description="Specialist agent for summarizing lengthy news content into concise bullet points.",
    instructions="""
    You are a news summarization specialist. Your job is to take lengthy news articles,
    reports, or content and create concise, informative summaries.
    
    You can:
    - Create bullet-point summaries of news articles
    - Extract key information and main points
    - Provide both extractive and abstractive summaries
    - Maintain factual accuracy while being concise
    
    Always preserve the essential facts and maintain objectivity.
    Focus on the most important information and present it clearly.
    """,
    model=get_chat_completion_model(),
    tools=[get_news_summary],
    output_type=NewsSummaryOutput
)

async def main():
    print("📝 Testing News Summarizer Agent...")
    print("=" * 60)
    
    user_context = UserContext()
    
    test_content = [
        """
        Breaking: Tech Giants Announce Collaboration on AI Safety Standards
        
        In a unprecedented move, major technology companies including Apple, Google, Microsoft, 
        and Meta have announced a joint initiative to develop comprehensive AI safety standards. 
        The collaboration, dubbed the "AI Safety Alliance," aims to create industry-wide guidelines 
        for the responsible development and deployment of artificial intelligence systems.
        
        The initiative comes amid growing concerns about AI safety, particularly as large language 
        models and generative AI tools become more powerful and widespread. The companies plan to 
        share research, establish common safety protocols, and work with regulators to ensure 
        AI systems are developed with appropriate safeguards.
        
        Key focus areas include preventing AI misuse, ensuring transparency in AI decision-making, 
        protecting user privacy, and addressing potential biases in AI systems. The alliance also 
        plans to invest $500 million in AI safety research over the next three years.
        """,
        
        """
        Global Climate Summit Reaches Historic Agreement
        
        After two weeks of intense negotiations, representatives from 195 countries have reached 
        a landmark agreement at the Global Climate Summit. The accord includes commitments to 
        reduce greenhouse gas emissions by 50% by 2030 and achieve net-zero emissions by 2050.
        
        The agreement also establishes a $100 billion annual fund to help developing nations 
        transition to clean energy and adapt to climate change impacts. Major provisions include 
        mandatory carbon pricing, forest protection initiatives, and technology sharing agreements.
        
        Environmental groups have hailed the agreement as a crucial step forward, while some 
        critics argue the timeline may be too ambitious given current economic challenges.
        """
    ]
    
    for i, content in enumerate(test_content, 1):
        print(f"\n📄 Summarizing Article {i}:")
        print("-" * 50)
        
        try:
            # Run the agent with the content
            response = await Runner.run(news_summarizer_agent, content, context=user_context)
            #response = await news_summarizer_agent.run(f"Please summarize this news content: {content}", user_context)
            print(f"📝 Summary:")
            
            if hasattr(response.final_output, 'summary_points'):
                for j, point in enumerate(response.final_output.summary_points, 1):
                    print(f"  {j}. {point.content}")
            else:
                print(f"  {response}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 50)
    
    print("\n✅ News Summarizer Agent testing completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())