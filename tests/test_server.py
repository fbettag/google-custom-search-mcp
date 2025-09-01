"""Live integration tests for Google Custom Search MCP server."""

import os
import pytest

from server import (
    search_google_custom_search,
    SearchParams,
    SearchResponse
)


class TestSearchGoogleCustomSearch:
    """Live integration tests with actual Google Custom Search API."""

    def test_search_success(self):
        """Test successful search operation with live Google API."""
        result = search_google_custom_search("python programming", 5)
        
        assert isinstance(result, SearchResponse)
        assert len(result.results) <= 5  # May get fewer results
        assert result.total_results >= 0
        assert result.search_time >= 0
        
        # Verify result structure
        if result.results:
            first_result = result.results[0]
            assert first_result.title
            assert first_result.link.startswith("http")
            assert first_result.snippet
            assert first_result.display_link

    def test_search_no_results_query(self):
        """Test search with a query that should return no results."""
        # Use a very specific query that likely returns no results
        result = search_google_custom_search("asdfghjkl1234567890zzzqqq", 5)
        
        assert isinstance(result, SearchResponse)
        assert len(result.results) == 0
        assert result.total_results == 0
        assert result.search_time >= 0

    def test_search_params_validation(self):
        """Test SearchParams validation."""
        params = SearchParams(query="test", num_results=5)
        assert params.query == "test"
        assert params.num_results == 5

    def test_default_num_results(self):
        """Test default number of results."""
        params = SearchParams(query="test")
        assert params.num_results == 10

    def test_num_results_validation(self):
        """Test number of results validation."""
        # Test minimum
        with pytest.raises(ValueError):
            SearchParams(query="test", num_results=0)
        
        # Test maximum  
        with pytest.raises(ValueError):
            SearchParams(query="test", num_results=101)


class TestMCPIntegration:
    """Test MCP server integration."""

    def test_mcp_tool_registration(self):
        """Test that the MCP tool is properly registered."""
        from server import mcp
        
        # Verify tool is registered
        assert "google_search" in mcp._tools
        tool_info = mcp._tools["google_search"]
        assert tool_info["name"] == "google_search"
        assert "Perform a Google Custom Search" in tool_info["description"]