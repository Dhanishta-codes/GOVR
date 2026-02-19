"""Research tools for finding company information"""

from tavily import TavilyClient
import agent.infra.config as config

def search_company_info(company_name: str) -> dict:
    """
    Search for company information using Tavily
    
    Args:
        company_name: Name of the company to research
        
    Returns:
        Dictionary with search results
    """
    if not config.TAVILY_API_KEY:
        return {
            "success": False,
            "error": "Tavily API key not configured"
        }
    
    try:
        client = TavilyClient(api_key=config.TAVILY_API_KEY)
        
        # Search for general company info
        query = f"{company_name} company products services"
        results = client.search(
            query=query,
            max_results=5,
            search_depth="advanced"
        )
        
        return {
            "success": True,
            "results": results.get("results", []),
            "query": query
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def search_company_news(company_name: str) -> dict:
    """
    Search for recent news about the company
    
    Args:
        company_name: Name of the company
        
    Returns:
        Dictionary with news results
    """
    if not config.TAVILY_API_KEY:
        return {
            "success": False,
            "error": "Tavily API key not configured"
        }
    
    try:
        client = TavilyClient(api_key=config.TAVILY_API_KEY)
        
        query = f"{company_name} news recent developments"
        results = client.search(
            query=query,
            max_results=3,
            days=30  # Last 30 days
        )
        
        return {
            "success": True,
            "results": results.get("results", []),
            "query": query
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def format_search_results(results: list) -> str:
    """
    Format search results into a readable string
    
    Args:
        results: List of search results from Tavily
        
    Returns:
        Formatted string of results
    """
    if not results:
        return "No results found."
    
    formatted = []
    for i, result in enumerate(results, 1):
        formatted.append(f"""
Result {i}:
Title: {result.get('title', 'N/A')}
Content: {result.get('content', 'N/A')}
URL: {result.get('url', 'N/A')}
---
        """)
    
    return "\n".join(formatted)
