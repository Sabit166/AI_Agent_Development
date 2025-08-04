import asyncio
import sys
import os

# Fix import path - go up two levels to reach src directory
current_dir = os.path.dirname(os.path.abspath(__file__))  # /src/main/
src_dir = os.path.dirname(current_dir)                   # /src/
project_root = os.path.dirname(src_dir)                  # /NewSense-1/

# Add src directory to Python path
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# FIXED: Import without 'src.' prefix since src is in the path
from agent.news_intelligence_agent import news_intelligence_agent
from models.user_context import UserContext
from agents import Runner

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
            
            # Handle different response types
            if hasattr(response.final_output, 'headlines'):
                for j, headline in enumerate(response.final_output.headlines[:5], 1):
                    print(f"  {j}. {headline.title}")
                    print(f"     Source: {headline.source} | Category: {headline.category}")
                    
            elif hasattr(response.final_output, 'verdict'):
                print(f"  Verdict: {response.final_output.verdict}")
                print(f"  Confidence: {response.final_output.confidence_level}")
                print(f"  Reasoning: {response.final_output.reasoning}")
                if hasattr(response.final_output, 'sources') and response.final_output.sources:
                    print(f"  Sources checked: {len(response.final_output.sources)}")
                    
            elif hasattr(response.final_output, 'summary_points'):
                for j, point in enumerate(response.final_output.summary_points, 1):
                    print(f"  {j}. {point.content}")
            
            # Handle NewsIntelligenceOutput properly
            elif hasattr(response.final_output, 'conversation_data') and response.final_output.conversation_data:
                conv_data = response.final_output.conversation_data
                print(f"  {conv_data.message}")
                if hasattr(conv_data, 'suggestions') and conv_data.suggestions:
                    print(f"  Suggestions: {', '.join(conv_data.suggestions)}")
                    
            elif hasattr(response.final_output, 'primary_response'):
                print(f"  {response.final_output.primary_response}")
                
            elif hasattr(response.final_output, 'message'):
                print(f"  {response.final_output.message}")
                if hasattr(response.final_output, 'suggestions') and response.final_output.suggestions:
                    print(f"  Suggestions: {', '.join(response.final_output.suggestions)}")
            
            else:
                # Extract clean message from verbose output
                response_str = str(response.final_output)
                if '"message":"' in response_str:
                    # Extract the message using string parsing
                    start = response_str.find('"message":"') + 11
                    end = response_str.find('","', start)
                    if end > start:
                        clean_message = response_str[start:end].replace('\\', '')
                        print(f"  {clean_message}")
                    else:
                        print(f"  Response received (type: {type(response.final_output).__name__})")
                else:
                    print(f"  Response received (type: {type(response.final_output).__name__})")

        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 50)
    
    print("\n✅ News Intelligence Agent testing completed!")

if __name__ == "__main__":
    asyncio.run(main())