"""
Marketing Search Tool for searching marketing trends, strategies, and competitor information.
"""
from typing import Dict, Any, List, Optional, Type
import logging
from datetime import datetime

from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from app.utils.search_utils import SearchService

# Set up logger
logger = logging.getLogger(__name__)

class MarketingSearchInput(BaseModel):
    """Input schema for the marketing search tool."""
    
    query: str = Field(..., description="Search query")
    search_type: str = Field("trends", description="Type of information to search for (trends, strategies, competitors)")
    industry: Optional[str] = Field(None, description="Industry or event type for the search")
    max_results: Optional[int] = Field(5, description="Maximum number of results to return")
    search_depth: Optional[str] = Field("basic", description="Depth of search (basic or advanced)")


class MarketingSearchTool(BaseTool):
    """Tool for searching for marketing trends, strategies, and competitor information."""
    
    name: str = "marketing_search_tool"
    description: str = "Search for marketing trends, strategies, or competitor information"
    args_schema: Type[MarketingSearchInput] = MarketingSearchInput
    
    def _run(self, 
             query: str, 
             search_type: str = "trends", 
             industry: Optional[str] = None,
             max_results: int = 5,
             search_depth: str = "basic") -> Dict[str, Any]:
        """
        Run the marketing search tool.
        
        Args:
            query: Search query
            search_type: Type of information to search for (trends, strategies, competitors)
            industry: Industry or event type for the search
            max_results: Maximum number of results to return
            search_depth: Depth of search (basic or advanced)
            
        Returns:
            Dictionary with search results
        """
        # Validate search_type
        valid_search_types = ["trends", "strategies", "competitors"]
        if search_type not in valid_search_types:
            return {
                "success": False,
                "error": f"Invalid search_type. Must be one of: {', '.join(valid_search_types)}",
                "query": query
            }
        
        # Format the query based on search type and industry
        formatted_query = query
        if industry and industry.lower() not in query.lower():
            formatted_query = f"{query} for {industry} events"
            
        if search_type == "trends":
            formatted_query = f"latest marketing trends {formatted_query}"
        elif search_type == "strategies":
            formatted_query = f"marketing strategies {formatted_query}"
        elif search_type == "competitors":
            formatted_query = f"competitor analysis {formatted_query}"
        
        logger.info(f"Marketing Search: {formatted_query} (type: {search_type})")
        
        # Perform the search
        search_service = SearchService()
        results = search_service.search(
            query=formatted_query,
            search_depth=search_depth,
            max_results=max_results,
            topic="news" if search_type == "trends" else "general"
        )
        
        # Format the results for the agent
        if results["success"]:
            # Process and structure the results based on search_type
            processed_results = self._process_results(results["results"], search_type)
            
            response = {
                "query": query,
                "formatted_query": formatted_query,
                "search_type": search_type,
                "results": processed_results,
                "total_found": results["total_found"],
                "success": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Marketing Search completed: {len(processed_results)} results found")
            return response
        else:
            logger.error(f"Marketing Search failed: {results.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": results.get("error", "Unknown error"),
                "query": query,
                "search_type": search_type
            }
    
    def _process_results(self, results: List[Dict[str, Any]], search_type: str) -> List[Dict[str, Any]]:
        """
        Process and structure the results based on search_type.
        
        Args:
            results: Raw search results
            search_type: Type of information being searched for
            
        Returns:
            Processed results
        """
        processed_results = []
        
        for result in results:
            processed_result = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "description": result.get("content", "")
            }
            
            if search_type == "trends":
                # Try to extract trend information
                content = result.get("content", "").lower()
                
                # Look for trend indicators
                trend_indicators = ["trend", "growing", "popular", "emerging", "latest", "new", "innovative"]
                trends = []
                
                sentences = content.split(". ")
                for sentence in sentences:
                    for indicator in trend_indicators:
                        if indicator in sentence.lower():
                            trends.append(sentence.strip())
                            break
                
                if trends:
                    processed_result["trends"] = list(set(trends))  # Remove duplicates
                
                # Try to extract date/year information to determine how recent the trend is
                year_indicators = ["2025", "2024", "2023", "this year", "last year", "recent"]
                for indicator in year_indicators:
                    if indicator in content:
                        for sentence in sentences:
                            if indicator in sentence.lower():
                                processed_result["recency_info"] = sentence.strip()
                                break
                
            elif search_type == "strategies":
                # Try to extract strategy information
                content = result.get("content", "").lower()
                
                # Look for strategy indicators
                strategy_indicators = ["strategy", "approach", "tactic", "method", "technique", "best practice", "tip"]
                strategies = []
                
                sentences = content.split(". ")
                for sentence in sentences:
                    for indicator in strategy_indicators:
                        if indicator in sentence.lower():
                            strategies.append(sentence.strip())
                            break
                
                if strategies:
                    processed_result["strategies"] = list(set(strategies))  # Remove duplicates
                
                # Look for effectiveness indicators
                effectiveness_indicators = ["effective", "success", "result", "impact", "roi", "conversion", "engagement"]
                for indicator in effectiveness_indicators:
                    if indicator in content:
                        for sentence in sentences:
                            if indicator in sentence.lower():
                                processed_result["effectiveness_info"] = sentence.strip()
                                break
            
            elif search_type == "competitors":
                # Try to extract competitor information
                content = result.get("content", "").lower()
                
                # Look for competitor indicators
                competitor_indicators = ["competitor", "competition", "rival", "industry leader", "market share", "alternative"]
                competitors = []
                
                sentences = content.split(". ")
                for sentence in sentences:
                    for indicator in competitor_indicators:
                        if indicator in sentence.lower():
                            competitors.append(sentence.strip())
                            break
                
                if competitors:
                    processed_result["competitor_info"] = list(set(competitors))  # Remove duplicates
                
                # Look for differentiation indicators
                differentiation_indicators = ["different", "unique", "stand out", "advantage", "strength", "weakness", "opportunity"]
                for indicator in differentiation_indicators:
                    if indicator in content:
                        for sentence in sentences:
                            if indicator in sentence.lower():
                                processed_result["differentiation_info"] = sentence.strip()
                                break
            
            processed_results.append(processed_result)
            
        return processed_results
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)
