from typing import Dict, Any, List, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.utils.search_utils import SearchService


class StakeholderSearchInput(BaseModel):
    """Input schema for the stakeholder search tool."""
    
    query: str = Field(..., description="The search query")
    max_results: int = Field(5, description="Maximum number of results to return")


class StakeholderSearchTool(BaseTool):
    """Tool for searching stakeholder related information."""
    
    name: str = "stakeholder_search_tool"
    description: str = "Search for stakeholder related information"
    args_schema: type = StakeholderSearchInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize search service when needed instead of as instance attribute
    
    def _run(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Run the stakeholder search tool.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with search results
        """
        # Define the stakeholder related topics to search for
        topics = [
            "speaker",
            "sponsor",
            "volunteer",
            "VIP",
            "stakeholder management",
            "stakeholder communication",
            "stakeholder engagement",
            "speaker requirements",
            "sponsor benefits",
            "volunteer coordination",
            "VIP experience",
            "stakeholder plan",
            "stakeholder relationship",
            "stakeholder feedback",
            "stakeholder satisfaction"
        ]
        
        # Enhance the query with stakeholder context
        enhanced_query = f"{query} (speaker OR sponsor OR volunteer OR VIP OR stakeholder)"
        
        # Search for documents
        search_service = SearchService()
        search_response = search_service.search(
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
