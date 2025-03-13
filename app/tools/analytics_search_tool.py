from typing import Dict, Any, List, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.utils.search_utils import SearchService


class AnalyticsSearchInput(BaseModel):
    """Input schema for the analytics search tool."""
    
    query: str = Field(..., description="The search query")
    max_results: int = Field(5, description="Maximum number of results to return")


class AnalyticsSearchTool(BaseTool):
    """Tool for searching analytics related information."""
    
    name: str = "analytics_search_tool"
    description: str = "Search for analytics related information"
    args_schema: type = AnalyticsSearchInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_service = SearchService()
    
    def _run(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Run the analytics search tool.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with search results
        """
        # Define the analytics related topics to search for
        topics = [
            "event analytics",
            "data collection",
            "metrics",
            "KPIs",
            "segmentation",
            "surveys",
            "feedback",
            "reporting",
            "ROI analysis",
            "attendee analytics",
            "engagement metrics",
            "satisfaction metrics",
            "data visualization",
            "insights",
            "performance analysis"
        ]
        
        # Enhance the query with analytics context
        enhanced_query = f"{query} (analytics OR metrics OR KPI OR data OR reporting OR insights)"
        
        # Search for documents
        search_response = self.search_service.search(
            query=enhanced_query,
            max_results=max_results
        )
        search_results = search_response.get("results", [])
        
        # Process and format the results
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                "title": result.get("title", "Untitled"),
                "content": result.get("content", ""),
                "relevance": result.get("relevance", 0.0),
                "source": result.get("source", "Unknown")
            })
        
        # Return the search results
        return {
            "query": query,
            "enhanced_query": enhanced_query,
            "results": formatted_results,
            "result_count": len(formatted_results),
            "topics": topics
        }
    
    async def _arun(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(query, max_results)
