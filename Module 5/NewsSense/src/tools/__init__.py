"""
Tools and utilities for News Intelligence System
"""

# Simple function_tool decorator replacement
def function_tool(func):
    """Simple decorator replacement for function_tool"""
    return func

# Try to import from external agents library if available
try:
    from agent import function_tool as external_function_tool
    # Use external one if available
    function_tool = external_function_tool
except ImportError:
    # Use our simple implementation
    pass

# Import tool modules with error handling
try:
    from .news_fetcher import get_trending_news
except ImportError:
    get_trending_news = None

try:
    from .fact_checker import get_fact_checking
except ImportError:
    get_fact_checking = None

try:
    from .summarizer import get_news_summary
except ImportError:
    get_news_summary = None

# Define what can be imported
__all__ = ['function_tool', 'get_trending_news', 'get_fact_checking', 'get_news_summary']