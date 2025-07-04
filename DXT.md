# DXT for MVG Störung MCP Server

This document provides the Developer Experience Toolkit (DXT) for the MVG Störung MCP Server.

## Overview

The MVG Störung MCP Server provides real-time, cached access to Munich Public Transport (MVG) disruption data.

## MCP Client Configuration

To connect your MCP client to this server, use the following configuration:

```json
{
  "mcpServers": {
    "mvg-stoerung": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "ghcr.io/rmoriz/mvg_stoerung_mcp:latest"
      ]
    }
  }
}
```

---

## Available Tools

### `get_mvg_incidents`

Get current MVG incidents (cached for 10+ minutes)

**Input Schema:**

```json
{
  "type": "object",
  "properties": {
    "force_refresh": {
      "type": "boolean",
      "description": "Force refresh cache even if not expired",
      "default": false
    }
  }
}
```

**Example Call:**

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_mvg_incidents",
    "arguments": {"force_refresh": false}
  }
}
```


---
### `get_cache_status`

Get information about the cache status

**Input Schema:**

```json
{
  "type": "object",
  "properties": {}
}
```

**Example Call:**

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_cache_status",
    "arguments": {}
  }
}
```


---
### `search_incidents`

Search incidents by line, title, or description

**Input Schema:**

```json
{
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
  "required": [
    "query"
  ]
}
```

**Example Call:**

```json
{
  "method": "tools/call",
  "params": {
    "name": "search_incidents",
    "arguments": {"query": "Aufzug", "line": "U3"}
  }
}
```


---

## Available Resources

### `mvg://incidents`

**Name:** MVG Incidents

**Description:** Current incidents from Munich Public Transport (MVG)

**MIME Type:** application/json

**Example Read:**

```json
{
  "method": "resources/read",
  "params": {
    "uri": "mvg://incidents"
  }
}
```


---
### `mvg://cache-info`

**Name:** Cache Information

**Description:** Information about the current cache status

**MIME Type:** application/json

**Example Read:**

```json
{
  "method": "resources/read",
  "params": {
    "uri": "mvg://cache-info"
  }
}
```


---
