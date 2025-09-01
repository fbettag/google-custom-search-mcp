"""Pytest configuration for Google Custom Search MCP tests."""

import os
import pytest


@pytest.fixture
autouse=True):
    """Automatically use this fixture for all tests to ensure required env vars."""
    # Check if we have the required environment variables for live testing
    required_vars = ["GOOGLE_SERVICE_ACCOUNT_BASE64", "GOOGLE_SEARCH_ENGINE_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        pytest.skip(f"Skipping live tests - missing environment variables: {', '.join(missing_vars)}")
    
    yield