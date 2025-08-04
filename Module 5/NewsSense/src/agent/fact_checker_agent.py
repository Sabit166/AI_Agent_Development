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
from models.output_format import FactCheckOutput
from config.openai_client import get_chat_completion_model
from tools.fact_checker import get_fact_checking


fact_checker_agent = Agent[UserContext](
    name="Fact Checking Specialist",
    handoff_description="Specialist agent for verifying claims and fact-checking using web search and RAG.",
    instructions="""
    You are a fact-checking specialist. Your job is to verify claims, statements, and news items
    using reliable sources and evidence-based analysis.
    
    You can:
    - Verify claims using web search and reliable sources
    - Analyze evidence and provide confidence ratings
    - Identify misinformation and provide corrections
    - Cite sources and provide reasoning for verdicts
    
    Always be objective, evidence-based, and cite your sources clearly.
    Provide confidence levels and explain your reasoning.
    """,
    model=get_chat_completion_model(),
    tools=[get_fact_checking],
    output_type=FactCheckOutput
)

async def main():
    print("🔍 Testing Fact Checker Agent...")
    print("=" * 60)
    
    user_context = UserContext()
    
    test_claims = [
        "The Earth is flat",
        "Vaccines cause autism",
        "Climate change is a natural phenomenon not caused by humans",
        "The 2020 US presidential election was rigged",
        "Drinking 8 glasses of water a day is necessary for good health"
    ]
    
    for i, claim in enumerate(test_claims, 1):
        print(f"\n🔍 Fact-checking claim {i}: {claim}")
        print("-" * 50)
        
        try:
            # Run the agent with the claim
            response = await Runner.run(fact_checker_agent, claim, context=user_context)
            print(f"🔍 Fact-check Result:")

            if hasattr(response.final_output, 'verdict'):
                print(f"  Verdict: {response.final_output.verdict}")
                print(f"  Confidence: {response.final_output.confidence_level}")
                print(f"  Reasoning: {response.final_output.reasoning}")
                if hasattr(response.final_output, 'sources') and response.final_output.sources:
                    print(f"  Sources checked: {len(response.final_output.sources)}")
            else:
                print(f"  {response}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 50)
    
    print("\n✅ Fact Checker Agent testing completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())