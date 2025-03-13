from typing import Dict, Any, List, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.utils.search_utils import SearchService


class FinancialSearchInput(BaseModel):
    """Input schema for the financial search tool."""
    
    query: str = Field(..., description="The search query")
    max_results: int = Field(5, description="Maximum number of results to return")


class FinancialSearchTool(BaseTool):
    """Tool for searching financial related information."""
    
    name: str = "financial_search_tool"
    description: str = "Search for financial related information"
    args_schema: type = FinancialSearchInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_service = SearchService()
    
    def _run(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Run the financial search tool.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with search results
        """
        # Define the financial related topics to search for
        topics = [
            "budget",
            "expense",
            "payment",
            "contract",
            "invoice",
            "financial report",
            "cost",
            "pricing",
            "vendor payment",
            "financial plan",
            "ROI",
            "revenue",
            "refund",
            "financial compliance",
            "tax"
        ]
        
        # Enhance the query with financial context
        enhanced_query = f"{query} (budget OR expense OR payment OR contract OR financial)"
        
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
