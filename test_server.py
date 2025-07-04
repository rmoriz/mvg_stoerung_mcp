import json
import pytest
from mvg_mcp_server import (
    MVGDataFetcher, 
    MVGCache, 
    get_incidents, 
    handle_call_tool,
    cache
)

@pytest.mark.asyncio
async def test_data_fetcher(mock_mvg_api):
    """Test the MVG data fetcher with a mocked API."""
    fetcher = MVGDataFetcher()
    try:
        incidents = await fetcher.fetch_incidents()
        assert len(incidents) == 1
        assert incidents[0]["title"] == "U-Bahn Störung"
    finally:
        await fetcher.close()

def test_cache():
    """Test the cache functionality."""
    local_cache = MVGCache(cache_duration_minutes=1)
    assert local_cache.is_expired()
    
    test_data = [{"id": 1, "title": "Test incident"}]
    local_cache.set(test_data)
    
    assert not local_cache.is_expired()
    assert local_cache.get() == test_data

@pytest.mark.asyncio
async def test_get_incidents_caching(mock_mvg_api):
    """Test the get_incidents function with caching."""
    # Clear global cache for predictable test
    cache._cached_data = None

    # First call should fetch from API
    incidents = await get_incidents()
    assert len(incidents) == 1
    assert mock_mvg_api.get("/").call_count == 1

    # Second call should use cache
    incidents2 = await get_incidents()
    assert len(incidents2) == 1
    assert mock_mvg_api.get("/").call_count == 1 # Should not have increased

@pytest.mark.asyncio
async def test_search_incidents(mock_mvg_api):
    """Test the search_incidents tool."""
    cache._cached_data = None # Clear cache

    # Search for "U-Bahn"
    search_args = {"query": "U-Bahn"}
    result_content = await handle_call_tool("search_incidents", search_args)
    result = json.loads(result_content[0].text)
    assert result["count"] == 1
    assert result["incidents"][0]["title"] == "U-Bahn Störung"

    # Search for something that doesn't exist
    search_args = {"query": "S-Bahn"}
    result_content = await handle_call_tool("search_incidents", search_args)
    result = json.loads(result_content[0].text)
    assert result["count"] == 0
