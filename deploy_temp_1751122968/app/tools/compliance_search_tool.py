"""
Compliance Search Tool for searching regulations, requirements, and security protocols.
"""
from typing import Dict, Any, List, Optional, Type
import logging
from datetime import datetime

from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from app.utils.search_utils import SearchService

# Set up logger
logger = logging.getLogger(__name__)

class ComplianceSearchInput(BaseModel):
    """Input schema for the compliance search tool."""
    
    query: str = Field(..., description="Search query")
    search_type: str = Field("regulation", description="Type of information to search for (regulation, security, data_protection)")
    location: Optional[str] = Field(None, description="Location/jurisdiction for the search")
    max_results: Optional[int] = Field(5, description="Maximum number of results to return")
    search_depth: Optional[str] = Field("advanced", description="Depth of search (basic or advanced)")


class ComplianceSearchTool(BaseTool):
    """Tool for searching for compliance and security information."""
    
    name: str = "compliance_search_tool"
    description: str = "Search for regulations, security protocols, or data protection requirements"
    args_schema: Type[ComplianceSearchInput] = ComplianceSearchInput
    
    def _run(self, 
             query: str, 
             search_type: str = "regulation", 
             location: Optional[str] = None,
             max_results: int = 5,
             search_depth: str = "advanced") -> Dict[str, Any]:
        """
        Run the compliance search tool.
        
        Args:
            query: Search query
            search_type: Type of information to search for (regulation, security, data_protection)
            location: Location/jurisdiction for the search
            max_results: Maximum number of results to return
            search_depth: Depth of search (basic or advanced)
            
        Returns:
            Dictionary with search results
        """
        # Validate search_type
        valid_search_types = ["regulation", "security", "data_protection"]
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
            
        if search_type == "regulation":
            formatted_query = f"event regulations {formatted_query}"
        elif search_type == "security":
            formatted_query = f"event security protocols {formatted_query}"
        elif search_type == "data_protection":
            formatted_query = f"data protection requirements {formatted_query}"
        
        logger.info(f"Compliance Search: {formatted_query} (type: {search_type})")
        
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
            
            logger.info(f"Compliance Search completed: {len(processed_results)} results found")
            return response
        else:
            logger.error(f"Compliance Search failed: {results.get('error', 'Unknown error')}")
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
            
            if search_type == "regulation":
                # Try to extract specific regulation information
                content = result.get("content", "").lower()
                
                # Look for requirement indicators
                requirement_indicators = ["must", "required", "mandatory", "compliance", "law", "regulation", "code"]
                requirements = []
                
                sentences = content.split(". ")
                for sentence in sentences:
                    for indicator in requirement_indicators:
                        if indicator in sentence.lower():
                            requirements.append(sentence.strip())
                            break
                
                if requirements:
                    processed_result["requirements"] = list(set(requirements))  # Remove duplicates
                
                # Look for authority information
                authority_indicators = ["authority", "department", "agency", "commission", "board", "office"]
                for indicator in authority_indicators:
                    if indicator in content:
                        # Find the sentence containing the indicator
                        for sentence in sentences:
                            if indicator in sentence.lower():
                                processed_result["authority_info"] = sentence.strip()
                                break
                
            elif search_type == "security":
                # Try to extract security protocol information
                content = result.get("content", "").lower()
                
                # Look for security measure indicators
                security_indicators = ["security", "safety", "emergency", "protocol", "procedure", "measure", "plan"]
                security_measures = []
                
                sentences = content.split(". ")
                for sentence in sentences:
                    for indicator in security_indicators:
                        if indicator in sentence.lower():
                            security_measures.append(sentence.strip())
                            break
                
                if security_measures:
                    processed_result["security_measures"] = list(set(security_measures))  # Remove duplicates
            
            elif search_type == "data_protection":
                # Try to extract data protection information
                content = result.get("content", "").lower()
                
                # Look for data protection indicators
                data_indicators = ["data", "privacy", "gdpr", "personal information", "consent", "processing", "breach"]
                data_requirements = []
                
                sentences = content.split(". ")
                for sentence in sentences:
                    for indicator in data_indicators:
                        if indicator in sentence.lower():
                            data_requirements.append(sentence.strip())
                            break
                
                if data_requirements:
                    processed_result["data_requirements"] = list(set(data_requirements))  # Remove duplicates
            
            processed_results.append(processed_result)
            
        return processed_results
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)
