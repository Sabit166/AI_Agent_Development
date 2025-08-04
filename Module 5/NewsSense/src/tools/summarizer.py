import os
import sys
import asyncio
from typing import List
from agents import function_tool

# Fix the import path FIRST, before any other imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)

# Add both src and project root to Python path
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# NOW we can import our modules (after fixing the path)
from config.openai_client import client, MODEL_NAME


@function_tool
async def get_news_summary(content: str) -> List[str]:
    """
    Summarizes lengthy news content into concise bullet points.
    """
    try:
        # Create summarization prompt
        summarization_prompt = f"""
        You are a news summarization expert. Summarize the following content into 3-5 concise bullet points.
        
        CONTENT TO SUMMARIZE:
        {content}
        
        Format your response as a list of bullet points starting with '•'.
        """
        
        # Use the OpenAI client to summarize
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a professional news summarizer."},
                {"role": "user", "content": summarization_prompt}
            ],
            max_tokens=300,
            temperature=0.1
        )
        #print(client.api_key)
        
        summary_text = response.choices[0].message.content
        
        # Split into bullet points and clean them
        summary_points = [
            point.strip() 
            for point in summary_text.strip().split('\n') 
            if point.strip()
        ]
        
        return summary_points
        
    except Exception as e:
        return [f"Error during summarization: {str(e)}"]

def main():
    print("🧪 Testing News Summarizer...")
    print("=" * 50)
    
    # Example news content
    content = """
    Breaking: Major technology companies announced a groundbreaking partnership today to develop 
    sustainable AI solutions. The collaboration between Apple, Google, and Microsoft aims to reduce 
    energy consumption in data centers by 40% over the next five years. Industry experts believe 
    this initiative could revolutionize how artificial intelligence systems are powered globally. 
    The partnership will focus on renewable energy integration, more efficient algorithms, and 
    advanced cooling systems for server farms.
    """
    
    print("📰 Original Content:")
    print(content.strip())
    print("\n" + "=" * 50)
    
    # Test the summarizer
    summary = asyncio.run(get_news_summary(content))
    
    print("📝 Summary Points:")
    for i, point in enumerate(summary, 1):
        print(f"{i}. {point}")
    
    print("=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    main()