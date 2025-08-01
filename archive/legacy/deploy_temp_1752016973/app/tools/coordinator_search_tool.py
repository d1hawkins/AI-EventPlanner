from typing import Dict, Any, List, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.utils.search_utils import SearchService


class CoordinatorSearchInput(BaseModel):
    """Input schema for the coordinator search tool."""
    
    query: str = Field(..., description="The search query")
    max_results: int = Field(5, description="Maximum number of results to return")


class CoordinatorSearchTool(BaseTool):
    """Tool for searching coordinator related information."""
    
    name: str = "coordinator_search_tool"
    description: str = "Search for coordinator related information"
    args_schema: type = CoordinatorSearchInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize the search service
        self._search_service = None
    
    @property
    def search_service(self):
        """Lazy initialization of search service to ensure it's created when needed."""
        if self._search_service is None:
            self._search_service = SearchService()
        return self._search_service
    
    def _run(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Run the coordinator search tool.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with search results
        """
        # Define the coordinator related topics to search for
        topics = [
            "event planning",
            "event coordination",
            "event management",
            "event requirements",
            "event proposal",
            "event delegation",
            "event monitoring",
            "event status",
            "event progress",
            "event timeline",
            "event budget",
            "event stakeholders",
            "event resources",
            "event success criteria",
            "event risks"
        ]
        
        # Enhance the query with coordinator context
        enhanced_query = f"{query} (event OR planning OR coordination OR management OR requirements OR proposal OR delegation OR monitoring)"
        
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
