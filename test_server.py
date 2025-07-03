#!/usr/bin/env python3
"""
Test script for MVG MCP Server
"""

import asyncio
import json
import sys
from mvg_mcp_server import MVGMCPServer, MVGDataFetcher, MVGCache


async def test_data_fetcher():
    """Test the MVG data fetcher"""
    print("Testing MVG Data Fetcher...")
    
    fetcher = MVGDataFetcher()
    try:
        # Test fetching raw data
        print("Fetching raw data from MVG API...")
        raw_data = await fetcher.fetch_raw_data()
        print(f"Raw data type: {type(raw_data)}")
        
        if isinstance(raw_data, list):
            print(f"Received {len(raw_data)} messages")
        elif isinstance(raw_data, dict):
            print(f"Received dict with keys: {list(raw_data.keys())}")
        
        # Test filtering incidents
        print("Filtering incidents...")
        incidents = fetcher.filter_incidents(raw_data)
        print(f"Found {len(incidents)} incidents")
        
        # Test enhancing data
        if incidents:
            print("Testing data enhancement...")
            enhanced = fetcher.enhance_incident_data(incidents[0])
            print(f"Enhanced incident keys: {list(enhanced.keys())}")
            
            # Show sample incident
            print("\nSample incident:")
            print(json.dumps(enhanced, indent=2, ensure_ascii=False)[:500] + "...")
        
        # Test full fetch_incidents method
        print("\nTesting full fetch_incidents method...")
        all_incidents = await fetcher.fetch_incidents()
        print(f"Total incidents fetched: {len(all_incidents)}")
        
    except Exception as e:
        print(f"Error testing data fetcher: {e}")
        return False
    finally:
        await fetcher.close()
    
    return True


def test_cache():
    """Test the cache functionality"""
    print("\nTesting MVG Cache...")
    
    cache = MVGCache(cache_duration_minutes=1)  # 1 minute for testing
    
    # Test empty cache
    print("Testing empty cache...")
    assert cache.is_expired() == True
    assert cache.get() is None
    
    cache_info = cache.get_cache_info()
    print(f"Empty cache info: {cache_info}")
    assert cache_info["status"] == "empty"
    
    # Test setting data
    print("Testing cache set...")
    test_data = [{"id": 1, "title": "Test incident"}]
    cache.set(test_data)
    
    assert cache.is_expired() == False
    cached_data = cache.get()
    assert cached_data == test_data
    
    cache_info = cache.get_cache_info()
    print(f"Filled cache info: {cache_info}")
    assert cache_info["status"] == "valid"
    assert cache_info["cached_items"] == 1
    
    print("Cache tests passed!")
    return True


async def test_mcp_server():
    """Test the MCP server functionality"""
    print("\nTesting MCP Server...")
    
    server = MVGMCPServer()
    
    try:
        # Test getting incidents
        print("Testing get_incidents...")
        incidents = await server.get_incidents()
        print(f"Retrieved {len(incidents)} incidents")
        
        # Test cache behavior
        print("Testing cache behavior...")
        cached_incidents = await server.get_incidents()  # Should use cache
        assert len(cached_incidents) == len(incidents)
        
        # Test force refresh
        print("Testing force refresh...")
        fresh_incidents = await server.get_incidents(force_refresh=True)
        print(f"Fresh incidents: {len(fresh_incidents)}")
        
        print("MCP Server tests passed!")
        return True
        
    except Exception as e:
        print(f"Error testing MCP server: {e}")
        return False
    finally:
        await server.cleanup()


async def main():
    """Run all tests"""
    print("Starting MVG MCP Server Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test data fetcher
    if await test_data_fetcher():
        tests_passed += 1
        print("✓ Data fetcher tests passed")
    else:
        print("✗ Data fetcher tests failed")
    
    # Test cache
    if test_cache():
        tests_passed += 1
        print("✓ Cache tests passed")
    else:
        print("✗ Cache tests failed")
    
    # Test MCP server
    if await test_mcp_server():
        tests_passed += 1
        print("✓ MCP server tests passed")
    else:
        print("✗ MCP server tests failed")
    
    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("All tests passed! 🎉")
        return 0
    else:
        print("Some tests failed! ❌")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))