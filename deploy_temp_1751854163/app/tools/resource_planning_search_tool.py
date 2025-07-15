"""
Resource Planning Search Tool for searching venues, service providers, and equipment.
"""
from typing import Dict, Any, List, Optional, Type
import logging
from datetime import datetime

from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from app.utils.search_utils import SearchService

# Set up logger
logger = logging.getLogger(__name__)

class ResourceSearchInput(BaseModel):
    """Input schema for the resource search tool."""
    
    query: str = Field(..., description="Search query")
    search_type: str = Field("venue", description="Type of resource to search for (venue, service_provider, equipment)")
    location: Optional[str] = Field(None, description="Location for the search")
    max_results: Optional[int] = Field(5, description="Maximum number of results to return")
    search_depth: Optional[str] = Field("basic", description="Depth of search (basic or advanced)")


class ResourcePlanningSearchTool(BaseTool):
    """Tool for searching for event resources."""
    
    name: str = "resource_planning_search_tool"
    description: str = "Search for venues, service providers, or equipment for events"
    args_schema: Type[ResourceSearchInput] = ResourceSearchInput
    
    def _run(self, 
             query: str, 
             search_type: str = "venue", 
             location: Optional[str] = None,
             max_results: int = 5,
             search_depth: str = "basic") -> Dict[str, Any]:
        """
        Run the resource search tool.
        
        Args:
            query: Search query
            search_type: Type of resource to search for (venue, service_provider, equipment)
            location: Location for the search
            max_results: Maximum number of results to return
            search_depth: Depth of search (basic or advanced)
            
        Returns:
            Dictionary with search results
        """
        # Validate search_type
        valid_search_types = ["venue", "service_provider", "equipment"]
        if search_type not in valid_search_types:
            return {
                "success": False,
                "error": f"Invalid search_type. Must be one of: {', '.join(valid_search_types)}",
                "query": query
            }
        
        # Format the query based on search type and location
        formatted_query = query
        if location and "in " + location not in query.lower() and location.lower() not in query.lower():
            formatted_query = f"{query} in {location}"
            
        if search_type == "venue":
            formatted_query = f"event venue {formatted_query}"
        elif search_type == "service_provider":
            formatted_query = f"event service provider {formatted_query}"
        elif search_type == "equipment":
            formatted_query = f"event equipment rental {formatted_query}"
        
        logger.info(f"Resource Planning Search: {formatted_query} (type: {search_type})")
        
        # Perform the search
        search_service = SearchService()
        results = search_service.search(
            query=formatted_query,
            search_depth=search_depth,
            max_results=max_results
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
            
            logger.info(f"Resource Planning Search completed: {len(processed_results)} results found")
            return response
        else:
            logger.error(f"Resource Planning Search failed: {results.get('error', 'Unknown error')}")
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
            search_type: Type of resource being searched for
            
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
            
            if search_type == "venue":
                # Extract potential venue information
                processed_result["venue_name"] = result.get("title", "").split(" - ")[0] if " - " in result.get("title", "") else result.get("title", "")
                
                # Try to extract capacity and location information from the content
                content = result.get("content", "").lower()
                
                # Look for capacity information
                capacity_indicators = ["capacity", "accommodate", "seats", "people", "guests"]
                for indicator in capacity_indicators:
                    if indicator in content:
                        # Find the sentence containing the indicator
                        sentences = content.split(". ")
                        for sentence in sentences:
                            if indicator in sentence:
                                processed_result["capacity_info"] = sentence.strip()
                                break
                
                # Look for location information
                if location := result.get("title", "").split(" - ")[-1] if " - " in result.get("title", "") else "":
                    processed_result["location"] = location
                
            elif search_type == "service_provider":
                # Extract potential service provider information
                processed_result["provider_name"] = result.get("title", "").split(" | ")[0] if " | " in result.get("title", "") else result.get("title", "")
                
                # Try to extract service type information
                content = result.get("content", "").lower()
                service_types = ["catering", "photography", "videography", "decoration", "entertainment", "audio", "lighting", "security"]
                
                found_services = []
                for service in service_types:
                    if service in content:
                        found_services.append(service)
                
                if found_services:
                    processed_result["service_types"] = found_services
            
            elif search_type == "equipment":
                # Try to extract equipment type and pricing information
                content = result.get("content", "").lower()
                
                # Look for pricing information
                price_indicators = ["price", "cost", "rate", "$", "dollar", "rental fee"]
                for indicator in price_indicators:
                    if indicator in content:
                        # Find the sentence containing the indicator
                        sentences = content.split(". ")
                        for sentence in sentences:
                            if indicator in sentence:
                                processed_result["pricing_info"] = sentence.strip()
                                break
            
            processed_results.append(processed_result)
            
        return processed_results
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)
