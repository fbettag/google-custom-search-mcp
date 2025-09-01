#!/usr/bin/env python3
"""Async Python MCP server for Google Custom Search."""

import asyncio
import base64
import json
import os
from typing import Optional, Any

from fastmcp import FastMCP, Context
from googleapiclient.discovery import build
from google.oauth2 import service_account
from pydantic import BaseModel, Field

# Initialize MCP server
mcp = FastMCP("google-custom-search")


class SearchParams(BaseModel):
    """Parameters for Google Custom Search."""
    
    query: str = Field(..., description="Search query")
    num_results: Optional[int] = Field(
        default=10, 
        ge=1, 
        le=100, 
        description="Number of results to return (1-100)"
    )


class SearchResult(BaseModel):
    """Single search result from Google Custom Search."""
    
    title: str = Field(..., description="Result title")
    link: str = Field(..., description="Result URL")
    snippet: str = Field(..., description="Result snippet")
    display_link: str = Field(..., description="Display URL")


class SearchResponse(BaseModel):
    """Response from Google Custom Search."""
    
    results: list[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results found")
    search_time: float = Field(..., description="Search time in seconds")


class GoogleSearchManager:
    """Manages Google Custom Search service connections and operations."""
    
    def __init__(self, search_engine_id: str, credentials: Any):
        """Initialize with search engine ID and credentials."""
        self.search_engine_id = search_engine_id
        self.service = build('customsearch', 'v1', credentials=credentials)
        self._cache = {}  # Simple cache for search results
    
    def search(self, query: str, num_results: int = 10) -> SearchResponse:
        """Perform a search using the Google Custom Search API."""
        # Check cache first
        cache_key = f"{query}:{num_results}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Execute search
        result = self.service.cse().list(
            q=query,
            cx=self.search_engine_id,
            num=min(num_results, 10)  # Google API max per request is 10
        ).execute()
        
        results = []
        for item in result.get("items", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                link=item.get("link", ""),
                snippet=item.get("snippet", ""),
                display_link=item.get("displayLink", "")
            ))
        
        response = SearchResponse(
            results=results,
            total_results=int(result.get("searchInformation", {}).get("totalResults", 0)),
            search_time=float(result.get("searchInformation", {}).get("searchTime", 0))
        )
        
        # Cache the result
        self._cache[cache_key] = response
        return response
    
    def clear_cache(self):
        """Clear the search results cache."""
        self._cache.clear()


# Global manager instance
google_search_manager: Optional[GoogleSearchManager] = None


def get_google_search_manager() -> GoogleSearchManager:
    """Get or create GoogleSearchManager instance."""
    global google_search_manager
    
    if google_search_manager is None:
        # Get configuration from environment
        search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        if not search_engine_id:
            raise ValueError("GOOGLE_SEARCH_ENGINE_ID environment variable is required")
        
        # Get credentials
        credentials = get_google_credentials()
        
        # Create manager
        google_search_manager = GoogleSearchManager(search_engine_id, credentials)
    
    return google_search_manager


def get_google_credentials():
    """Get Google service account credentials from environment."""
    service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    service_account_base64 = os.getenv("GOOGLE_SERVICE_ACCOUNT_BASE64")
    
    if not service_account_file and not service_account_base64:
        raise ValueError(
            "Either GOOGLE_SERVICE_ACCOUNT_FILE or GOOGLE_SERVICE_ACCOUNT_BASE64 "
            "environment variable is required"
        )
    
    # Handle base64 encoded service account (for CI/CD)
    if service_account_base64:
        try:
            service_account_info = json.loads(base64.b64decode(service_account_base64).decode('utf-8'))
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=['https://www.googleapis.com/auth/cse']
            )
        except (ValueError, base64.binascii.Error) as e:
            raise ValueError(f"Invalid base64 encoded service account: {e}")
    
    # Handle file path (for local development)
    elif service_account_file:
        if not os.path.exists(service_account_file):
            raise ValueError(f"Service account file not found: {service_account_file}")
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/cse']
        )
    
    return credentials


def get_google_service():
    """Create and return Google Custom Search service with service account auth."""
    
    service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    service_account_base64 = os.getenv("GOOGLE_SERVICE_ACCOUNT_BASE64")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    if not search_engine_id:
        raise ValueError("GOOGLE_SEARCH_ENGINE_ID environment variable is required")
    
    if not service_account_file and not service_account_base64:
        raise ValueError(
            "Either GOOGLE_SERVICE_ACCOUNT_FILE or GOOGLE_SERVICE_ACCOUNT_BASE64 "
            "environment variable is required"
        )
    
    # Handle base64 encoded service account (for CI/CD)
    if service_account_base64:
        try:
            service_account_info = json.loads(base64.b64decode(service_account_base64).decode('utf-8'))
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=['https://www.googleapis.com/auth/cse']
            )
        except (ValueError, base64.binascii.Error) as e:
            raise ValueError(f"Invalid base64 encoded service account: {e}")
    
    # Handle file path (for local development)
    elif service_account_file:
        if not os.path.exists(service_account_file):
            raise ValueError(f"Service account file not found: {service_account_file}")
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/cse']
        )
    
    # Build the Custom Search service
    service = build('customsearch', 'v1', credentials=credentials)
    return service


def search_google_custom_search(
    query: str, 
    num_results: int = 10
) -> SearchResponse:
    """Perform Google Custom Search with service account authentication."""
    
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    service = get_google_service()
    
    # Execute search
    result = service.cse().list(
        q=query,
        cx=search_engine_id,
        num=min(num_results, 10)  # Google API max per request is 10
    ).execute()
    
    results = []
    for item in result.get("items", []):
        results.append(SearchResult(
            title=item.get("title", ""),
            link=item.get("link", ""),
            snippet=item.get("snippet", ""),
            display_link=item.get("displayLink", "")
        ))
    
    return SearchResponse(
        results=results,
        total_results=int(result.get("searchInformation", {}).get("totalResults", 0)),
        search_time=float(result.get("searchInformation", {}).get("searchTime", 0))
    )


@mcp.tool()
async def google_search(params: SearchParams) -> SearchResponse:
    """
    Perform a Google Custom Search.
    
    Requires either:
    - GOOGLE_SERVICE_ACCOUNT_FILE (file path) for local development
    - GOOGLE_SERVICE_ACCOUNT_BASE64 (base64 encoded JSON) for CI/CD
    And GOOGLE_SEARCH_ENGINE_ID environment variable.
    """
    manager = get_google_search_manager()
    return manager.search(params.query, params.num_results or 10)


class ClearCacheResponse(BaseModel):
    """Response from clearing cache."""
    success: bool = Field(default=True, description="Operation success status")
    message: str = Field(..., description="Status message")


@mcp.tool()
async def clear_search_cache() -> ClearCacheResponse:
    """
    Clear the search results cache.
    """
    manager = get_google_search_manager()
    manager.clear_cache()
    return ClearCacheResponse(success=True, message="Search cache cleared")


async def main():
    """Run the MCP server."""
    # Validate required environment variables
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    service_account_base64 = os.getenv("GOOGLE_SERVICE_ACCOUNT_BASE64")
    
    if not search_engine_id:
        print("Error: GOOGLE_SEARCH_ENGINE_ID environment variable is required")
        print("Example: GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id")
        return
    
    if not service_account_file and not service_account_base64:
        print("Error: Either GOOGLE_SERVICE_ACCOUNT_FILE or GOOGLE_SERVICE_ACCOUNT_BASE64 environment variable is required")
        print("Example: GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/service-account.json")
        return
    
    if service_account_file:
        print(f"Starting Google Custom Search MCP Server with file-based authentication")
    else:
        print(f"Starting Google Custom Search MCP Server with base64-encoded authentication")
    
    await mcp.run()


if __name__ == "__main__":
    asyncio.run(main())