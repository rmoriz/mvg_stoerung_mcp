#!/usr/bin/env python3
"""
MCP Server for MVG Störung (Munich Public Transport Disruptions)
Provides cached access to MVG incident data with at least 10-minute caching
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
)
from pydantic import BaseModel


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CachedData(BaseModel):
    """Model for cached MVG data"""
    data: List[Dict[str, Any]]
    timestamp: datetime
    expires_at: datetime


class MVGCache:
    """Simple in-memory cache for MVG data with 10+ minute expiration"""
    
    def __init__(self, cache_duration_minutes: int = 10):
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self._cached_data: Optional[CachedData] = None
    
    def is_expired(self) -> bool:
        """Check if cached data is expired"""
        if self._cached_data is None:
            return True
        return datetime.now() >= self._cached_data.expires_at
    
    def get(self) -> Optional[List[Dict[str, Any]]]:
        """Get cached data if not expired"""
        if self.is_expired():
            return None
        return self._cached_data.data
    
    def set(self, data: List[Dict[str, Any]]) -> None:
        """Cache new data with expiration"""
        now = datetime.now()
        self._cached_data = CachedData(
            data=data,
            timestamp=now,
            expires_at=now + self.cache_duration
        )
        logger.info(f"Cached {len(data)} incidents, expires at {self._cached_data.expires_at}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cache status"""
        if self._cached_data is None:
            return {"status": "empty", "cached_items": 0}
        
        return {
            "status": "expired" if self.is_expired() else "valid",
            "cached_items": len(self._cached_data.data),
            "cached_at": self._cached_data.timestamp.isoformat(),
            "expires_at": self._cached_data.expires_at.isoformat(),
            "cache_duration_minutes": self.cache_duration.total_seconds() / 60
        }


class MVGDataFetcher:
    """Fetches and processes MVG disruption data"""
    
    MVG_API_URL = "https://www.mvg.de/api/bgw-pt/v3/messages"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def fetch_raw_data(self) -> Dict[str, Any]:
        """Fetch raw data from MVG API"""
        try:
            response = await self.client.get(self.MVG_API_URL)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Error fetching data from MVG API: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            raise
    
    def filter_incidents(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter messages to return only INCIDENT type elements"""
        incidents = []
        
        # Handle different possible data structures
        messages = []
        if isinstance(data, list):
            messages = data
        elif isinstance(data, dict):
            # Try common keys where messages might be stored
            for key in ["messages", "data", "items", "results"]:
                if key in data and isinstance(data[key], list):
                    messages = data[key]
                    break
            else:
                # If no common key found, check if the dict itself contains type field
                if "type" in data:
                    messages = [data]
        
        # Filter for INCIDENT type
        for message in messages:
            if isinstance(message, dict) and message.get("type") == "INCIDENT":
                incidents.append(message)
        
        return incidents
    
    def format_timestamp(self, timestamp: int) -> str:
        """Convert Unix timestamp (milliseconds) to readable format"""
        try:
            dt = datetime.fromtimestamp(timestamp / 1000)
            return dt.strftime("%d.%m.%Y %H:%M")
        except (ValueError, OSError):
            return str(timestamp)
    
    def enhance_incident_data(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Add human-readable fields to incident data"""
        enhanced = incident.copy()
        
        # Add readable timestamps
        if "publication" in enhanced and isinstance(enhanced["publication"], int):
            enhanced["publication_readable"] = self.format_timestamp(enhanced["publication"])
        
        if "validFrom" in enhanced and isinstance(enhanced["validFrom"], int):
            enhanced["validFrom_readable"] = self.format_timestamp(enhanced["validFrom"])
        
        if "validTo" in enhanced and isinstance(enhanced["validTo"], int):
            enhanced["validTo_readable"] = self.format_timestamp(enhanced["validTo"])
        
        return enhanced
    
    async def fetch_incidents(self) -> List[Dict[str, Any]]:
        """Fetch and process incident data"""
        raw_data = await self.fetch_raw_data()
        incidents = self.filter_incidents(raw_data)
        
        # Enhance each incident with readable timestamps
        enhanced_incidents = [self.enhance_incident_data(incident) for incident in incidents]
        
        logger.info(f"Fetched {len(enhanced_incidents)} incidents from MVG API")
        return enhanced_incidents
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Create server instance
server = Server("mvg-stoerung")

# Initialize components
cache = MVGCache(cache_duration_minutes=10)
fetcher = MVGDataFetcher()


async def get_incidents(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Get incidents with caching"""
    if not force_refresh:
        cached_data = cache.get()
        if cached_data is not None:
            logger.info(f"Returning {len(cached_data)} cached incidents")
            return cached_data
    
    # Fetch fresh data
    logger.info("Fetching fresh data from MVG API")
    incidents = await fetcher.fetch_incidents()
    cache.set(incidents)
    return incidents


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="mvg://incidents",
            name="MVG Incidents",
            description="Current incidents from Munich Public Transport (MVG)",
            mimeType="application/json",
        ),
        Resource(
            uri="mvg://cache-info",
            name="Cache Information",
            description="Information about the current cache status",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read resource content"""
    if uri == "mvg://incidents":
        incidents = await get_incidents()
        return json.dumps(incidents, indent=2, ensure_ascii=False)
    elif uri == "mvg://cache-info":
        cache_info = cache.get_cache_info()
        return json.dumps(cache_info, indent=2, ensure_ascii=False)
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_mvg_incidents",
            description="Get current MVG incidents (cached for 10+ minutes)",
            inputSchema={
                "type": "object",
                "properties": {
                    "force_refresh": {
                        "type": "boolean",
                        "description": "Force refresh cache even if not expired",
                        "default": False
                    }
                }
            },
        ),
        Tool(
            name="get_cache_status",
            description="Get information about the cache status",
            inputSchema={
                "type": "object",
                "properties": {}
            },
        ),
        Tool(
            name="search_incidents",
            description="Search incidents by line, title, or description",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (searches in title, description, and line labels)"
                    },
                    "line": {
                        "type": "string",
                        "description": "Filter by specific line (e.g., 'U6', 'S1', 'Bus 100')"
                    }
                },
                "required": ["query"]
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    if name == "get_mvg_incidents":
        force_refresh = arguments.get("force_refresh", False)
        incidents = await get_incidents(force_refresh=force_refresh)
        
        result = {
            "incidents": incidents,
            "count": len(incidents),
            "cache_info": cache.get_cache_info()
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    
    elif name == "get_cache_status":
        cache_info = cache.get_cache_info()
        return [TextContent(
            type="text",
            text=json.dumps(cache_info, indent=2, ensure_ascii=False)
        )]
    
    elif name == "search_incidents":
        query = arguments.get("query", "").lower()
        line_filter = arguments.get("line", "").upper()
        
        incidents = await get_incidents()
        filtered_incidents = []
        
        for incident in incidents:
            # Search in title and description
            title_match = query in incident.get("title", "").lower()
            desc_match = query in incident.get("description", "").lower()
            
            # Search in line labels
            line_match = False
            if "lines" in incident:
                for line in incident["lines"]:
                    if isinstance(line, dict) and "label" in line:
                        if query in line["label"].lower():
                            line_match = True
                            break
            
            # Apply line filter if specified
            line_filter_match = True
            if line_filter:
                line_filter_match = False
                if "lines" in incident:
                    for line in incident["lines"]:
                        if isinstance(line, dict) and "label" in line:
                            if line_filter in line["label"].upper():
                                line_filter_match = True
                                break
            
            if (title_match or desc_match or line_match) and line_filter_match:
                filtered_incidents.append(incident)
        
        result = {
            "incidents": filtered_incidents,
            "count": len(filtered_incidents),
            "query": arguments.get("query"),
            "line_filter": arguments.get("line"),
            "total_incidents": len(incidents)
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point"""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mvg-stoerung",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except KeyboardInterrupt:
        logger.info("Server interrupted")
    finally:
        await fetcher.close()


if __name__ == "__main__":
    asyncio.run(main())