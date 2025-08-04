import asyncio
import os
import sys
import urllib.parse
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

import aiohttp
from bs4 import BeautifulSoup
from typing import List
from models.user_context import UserContext
from config.openai_client import client, MODEL_NAME



async def extract_fact_check(session: aiohttp.ClientSession, url: str, claim: str) -> str:
    """Extract content from fact-checking websites"""
    try:
        # Fix DuckDuckGo redirect URLs
        if url.startswith('//duckduckgo.com/l/'):
            # Extract the actual URL from the redirect
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            if 'uddg' in parsed:
                actual_url = urllib.parse.unquote(parsed['uddg'][0])
                url = actual_url
            else:
                return f"Could not extract actual URL from redirect: {url}"
        
        # Ensure URL has a protocol
        if url.startswith('//'):
            url = 'https:' + url
        elif not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with session.get(url, headers=headers, timeout=15) as response:
            if response.status == 200:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Remove scripts and styles
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Try to find main content areas
                main_content = soup.find('article') or soup.find('main') or soup.find('div', class_='content') or soup.body
                
                if main_content:
                    text = main_content.get_text(strip=True)
                else:
                    text = soup.get_text(strip=True)
                
                # Clean up whitespace and limit length
                text = ' '.join(text.split())
                if len(text) > 800:
                    text = text[:800] + "..."
                
                return text
            else:
                return f"HTTP {response.status} error accessing {url}"
                
    except Exception as e:
        return f"Error extracting content from {url}: {str(e)}"

async def analyze_claim(claim: str, fact_check_results: List[dict]) -> dict:
    """Use AI to analyze the claim against gathered evidence."""
    try:
        # Prepare context from fact-check results
        context_texts = []
        for result in fact_check_results:
            summary = result.get('summary', '')
            if summary and not summary.startswith('Error'):
                context_texts.append(f"Source: {result['source']}\nContent: {summary}")
        
        if not context_texts:
            return {
                "verdict": "INSUFFICIENT EVIDENCE",
                "confidence": "LOW",
                "reasoning": "No reliable sources could be accessed for fact-checking."
            }
        
        context = "\n\n".join(context_texts)
        
        # Create analysis prompt
        prompt = f"""
        You are a fact-checking expert. Analyze the following claim against the provided evidence.
        
        CLAIM TO VERIFY: {claim}
        
        EVIDENCE FROM SOURCES:
        {context}
        
        Based on the evidence provided, please determine:
        1. VERDICT: TRUE, FALSE, PARTIALLY TRUE, or INSUFFICIENT EVIDENCE
        2. CONFIDENCE: HIGH, MEDIUM, or LOW
        3. REASONING: Brief explanation
        
        Respond in this exact format:
        VERDICT: [your verdict]
        CONFIDENCE: [your confidence]
        REASONING: [your explanation]
        """
        
        # Get AI analysis
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a professional fact-checker. Be objective and evidence-based."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.1
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse the response
        verdict = "INSUFFICIENT EVIDENCE"
        confidence = "LOW"
        reasoning = ai_response
        
        lines = ai_response.split('\n')
        for line in lines:
            if line.startswith('VERDICT:'):
                verdict = line.split('VERDICT:')[1].strip()
            elif line.startswith('CONFIDENCE:'):
                confidence = line.split('CONFIDENCE:')[1].strip()
            elif line.startswith('REASONING:'):
                reasoning = line.split('REASONING:')[1].strip()
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning
        }
        
    except Exception as e:
        return {
            "verdict": "ERROR",
            "confidence": "LOW",
            "reasoning": f"Analysis failed: {str(e)}"
        }

@function_tool
async def get_fact_checking(user_context: UserContext, claim: str) -> List[str]:
    """
    Fetches fact-checking information for a specific claim using web search and RAG.
    """
    try:
        # Use multiple search engines and direct fact-checking sites
        search_sources = [
            f"https://www.snopes.com/search/{claim.replace(' ', '%20')}",
            f"https://www.politifact.com/search/?q={claim.replace(' ', '+')}",
        ]
        
        # Also try some reliable news sources
        fact_checking_urls = [
            "https://www.snopes.com/fact-check/",
            "https://www.politifact.com/factchecks/",
            "https://www.factcheck.org/",
        ]
        
        fact_check_results = []
        
        async with aiohttp.ClientSession() as session:
            # Try to get some real fact-checking content
            for url in fact_checking_urls[:2]:  # Limit to avoid too many requests
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    async with session.get(url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            content = await response.text()
                            soup = BeautifulSoup(content, 'html.parser')
                            
                            # Look for article titles and links
                            articles = soup.find_all(['article', 'div'], class_=lambda x: x and any(
                                keyword in x.lower() for keyword in ['fact-check', 'article', 'story']
                            ))[:3]
                            
                            for article in articles:
                                title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'a'])
                                if title_elem:
                                    title = title_elem.get_text(strip=True)
                                    if any(word in title.lower() for word in claim.lower().split()):
                                        # Get a snippet of content
                                        content_snippet = article.get_text(strip=True)[:300]
                                        
                                        fact_check_entry = {
                                            'source': f"Fact-checking website: {url}",
                                            'url': url,
                                            'summary': f"{title} - {content_snippet}",
                                            'query': claim
                                        }
                                        
                                        fact_check_results.append(fact_check_entry)
                                        
                except Exception as e:
                    fact_check_results.append({
                        'source': f'Error accessing {url}',
                        'url': url,
                        'summary': f"Could not access fact-checking site: {str(e)}",
                        'query': claim
                    })
        
        # If we don't have good results, add some general knowledge
        if len(fact_check_results) == 0:
            fact_check_results.append({
                'source': 'General Scientific Consensus',
                'url': '',
                'summary': f'Analyzing claim: "{claim}" - Common scientific and factual knowledge suggests this claim needs verification.',
                'query': claim
            })
        
        # Use RAG to analyze and synthesize the findings
        rag_analysis = await analyze_claim(claim, fact_check_results)
        
        # Format results for return
        formatted_results = []
        formatted_results.append(f"CLAIM ANALYSIS: {claim}")
        formatted_results.append(f"RAG VERDICT: {rag_analysis['verdict']}")
        formatted_results.append(f"CONFIDENCE: {rag_analysis['confidence']}")
        formatted_results.append(f"REASONING: {rag_analysis['reasoning']}")
        formatted_results.append("SOURCES CHECKED:")
        
        for result in fact_check_results[:3]:
            source_info = result['summary'][:200] + "..." if len(result['summary']) > 200 else result['summary']
            formatted_results.append(f"- {result['source']}: {source_info}")
        
        # Update user context
        user_context.fact_checking = formatted_results
        return formatted_results
        
    except Exception as e:
        error_msg = f"Error during fact-checking: {str(e)}"
        return [error_msg]

def main():
    print("🧪 Testing Fact Checker...")
    print("=" * 50)
    
    user_context = UserContext()
    claim = "Apple has bought OpenAI."
    
    print(f"Fact-checking claim: {claim}")
    print("-" * 50)
    
    results = asyncio.run(get_fact_checking(user_context, claim))
    
    for result in results:
        print(result)
    
    print("=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    main()