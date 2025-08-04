import sys
import os
import asyncio
from agents import function_tool

# Fix the import path FIRST
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)

# Add both src and project root to Python path
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# NOW import modules (after path is fixed)
import aiohttp
import feedparser
from typing import List
from models.user_context import UserContext


@function_tool
async def get_trending_news(user_context: UserContext) -> List[str]:
    """
    Fetches trending news headlines from Google News RSS feed.
    Returns a list of news headlines with sources.
    """
    try:
        # Google News RSS feeds by category
        news_feeds = {
            "general": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
            "business": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZ4ZERBU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
            "technology": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
            "science": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en"
        }
        
        headlines = []
        
        async with aiohttp.ClientSession() as session:
            for category, url in news_feeds.items():
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            content = await response.text()
                            # Parse RSS feed
                            feed = feedparser.parse(content)
                            
                            # Extract headlines (limit to 5 per category)
                            for entry in feed.entries[:5]:
                                title = entry.title
                                link = entry.link
                                published = entry.get('published', 'Unknown time')
                                source = entry.get('source', {}).get('title', 'Unknown source')
                                
                                headline = f"[{category.upper()}] {title} - {source} ({published})"
                                headlines.append(headline)
                                
                except Exception as e:
                    headlines.append(f"Error fetching {category} news: {str(e)}")
        
        # Update user context
        user_context.trending_news = headlines
        return headlines
        
    except Exception as e:
        error_msg = f"Error fetching trending news: {str(e)}"
        return [error_msg]

def main():
    print("🧪 Testing News Fetcher...")
    print("=" * 50)
    
    user_context = UserContext()
    trending_news = asyncio.run(get_trending_news(user_context))
    
    print(f"📰 Fetched {len(trending_news)} news items:")
    print("-" * 50)
    
    for i, news in enumerate(trending_news, 1):
        print(f"{i}. {news}")
    
    print("-" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    main()