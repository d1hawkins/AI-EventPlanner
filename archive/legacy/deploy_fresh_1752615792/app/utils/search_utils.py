"""
Search utilities module for performing internet searches using Tavily API.
"""
import logging
from typing import Dict, Any, List, Optional

from app import config

# Set up logger
logger = logging.getLogger(__name__)

class SearchService:
    """Service for performing internet searches using Tavily API."""
    
    def __init__(self):
        """Initialize the search service with API key from config."""
        self.api_key = config.TAVILY_API_KEY
        self.search_enabled = bool(self.api_key)
        
        if not self.search_enabled:
            logger.warning("Tavily API key not set. Search functionality is disabled.")
        else:
            # Import Tavily client only if API key is available
            try:
                from tavily import TavilyClient
                self.client = TavilyClient(api_key=self.api_key)
                logger.info("Tavily search client initialized successfully.")
            except ImportError:
                logger.error("Failed to import tavily-python. Make sure it's installed.")
                self.search_enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize Tavily client: {str(e)}")
                self.search_enabled = False
    
    def search(self, 
               query: str, 
               search_depth: str = "basic", 
               max_results: int = 5, 
               include_domains: Optional[List[str]] = None, 
               exclude_domains: Optional[List[str]] = None,
               topic: str = "general") -> Dict[str, Any]:
        """
        Perform a search query using Tavily API.
        
        Args:
            query: Search query string
            search_depth: Depth of search ("basic" or "advanced")
            max_results: Maximum number of results to return
            include_domains: List of domains to include in search
            exclude_domains: List of domains to exclude from search
            topic: The category of search ("general" or "news")
            
        Returns:
            Dictionary with search results or error information
        """
        if not self.search_enabled:
            return {
                "success": False,
                "error": "Search functionality is disabled due to missing API key",
                "query": query,
                "results": []
            }
        
        try:
            logger.info(f"Performing search: '{query}' (depth: {search_depth}, topic: {topic})")
            
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_domains=include_domains or [],
                exclude_domains=exclude_domains or [],
                topic=topic
            )
            
            results = response.get("results", [])
            logger.info(f"Search completed. Found {len(results)} results.")
            
            return {
                "results": results,
                "query": query,
                "total_found": len(results),
                "success": True
            }
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": []
            }
    
    def extract_content(self, urls: List[str], extract_depth: str = "basic") -> Dict[str, Any]:
        """
        Extract content from specified URLs using Tavily API.
        
        Args:
            urls: List of URLs to extract content from
            extract_depth: Depth of extraction ("basic" or "advanced")
            
        Returns:
            Dictionary with extracted content or error information
        """
        if not self.search_enabled:
            return {
                "success": False,
                "error": "Search functionality is disabled due to missing API key",
                "urls": urls,
                "results": []
            }
        
        try:
            logger.info(f"Extracting content from {len(urls)} URLs (depth: {extract_depth})")
            
            results = []
            for url in urls:
                try:
                    response = self.client.extract(
                        url=url,
                        extract_depth=extract_depth
                    )
                    results.append({
                        "url": url,
                        "content": response.get("content", ""),
                        "title": response.get("title", ""),
                        "success": True
                    })
                except Exception as url_error:
                    logger.error(f"Error extracting content from {url}: {str(url_error)}")
                    results.append({
                        "url": url,
                        "error": str(url_error),
                        "success": False
                    })
            
            successful_extractions = sum(1 for r in results if r.get("success", False))
            logger.info(f"Content extraction completed. Successfully extracted {successful_extractions}/{len(urls)} URLs.")
            
            return {
                "results": results,
                "urls": urls,
                "total_processed": len(urls),
                "total_successful": successful_extractions,
                "success": True
            }
        except Exception as e:
            logger.error(f"Content extraction error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "urls": urls,
                "results": []
            }
