# MVG MCP Server Usage Guide

## Quick Start

1. **Start the server:**
   ```bash
   ./start_server.sh
   ```

2. **Or manually:**
   ```bash
   source venv/bin/activate
   python3 mvg_mcp_server.py
   ```

## Available Tools

### 1. Get MVG Incidents
```json
{
  "name": "get_mvg_incidents",
  "arguments": {
    "force_refresh": false
  }
}
```

**Response:**
```json
{
  "incidents": [...],
  "count": 5,
  "cache_info": {
    "status": "valid",
    "cached_items": 5,
    "cached_at": "2024-01-15T10:30:00",
    "expires_at": "2024-01-15T10:40:00",
    "cache_duration_minutes": 10
  }
}
```

### 2. Search Incidents
```json
{
  "name": "search_incidents",
  "arguments": {
    "query": "verspätung",
    "line": "U6"
  }
}
```

### 3. Get Cache Status
```json
{
  "name": "get_cache_status",
  "arguments": {}
}
```

## Available Resources

### 1. Current Incidents
- **URI:** `mvg://incidents`
- **Type:** JSON
- **Description:** All current MVG incidents

### 2. Cache Information
- **URI:** `mvg://cache-info`
- **Type:** JSON
- **Description:** Current cache status and statistics

## Example Incident Data

```json
{
  "title": "Verspätungen nach einer bereits behobenen Störung",
  "description": "Liebe Fahrgäste,<br>nach einer bereits behobenen Störung...",
  "publication": 1751525520000,
  "publication_readable": "03.01.2025 10:32",
  "validFrom": 1751525520000,
  "validFrom_readable": "03.01.2025 10:32",
  "validTo": 1751529120000,
  "validTo_readable": "03.01.2025 11:32",
  "type": "INCIDENT",
  "provider": "MVG",
  "lines": [
    {
      "label": "U6",
      "transportType": "UBAHN",
      "network": "swm",
      "divaId": "010U6",
      "sev": false
    }
  ]
}
```

## Cache Behavior

- **Duration:** 10 minutes minimum
- **Auto-refresh:** When cache expires
- **Force refresh:** Use `force_refresh: true` parameter
- **Status tracking:** Available via cache status tool

## Transport Types

- `UBAHN`: U-Bahn (Subway)
- `SBAHN`: S-Bahn (Suburban train)
- `BUS`: Bus
- `TRAM`: Tram/Streetcar

## Error Handling

The server handles:
- Network timeouts
- API unavailability
- Invalid responses
- Cache expiration
- Missing data

## Integration

### With MCP-compatible clients
Add to your MCP configuration:

```json
{
  "mcpServers": {
    "mvg-stoerung": {
      "command": "python3",
      "args": ["mvg_mcp_server.py"],
      "cwd": "/path/to/mvg_stoerung_mcp"
    }
  }
}
```

### Programmatic access
See `example_client.py` for a complete example of how to interact with the server programmatically.

---

*This usage guide is for informational purposes only. The data is provided by MVG and is subject to change.*

## Disclaimer

This project is not an official MVG project, not endorsed or recommended. Please ask MVG for permission prior to using it.
