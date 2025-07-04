

import json
import asyncio
from mcp.server import Server

async def generate_dxt_markdown(server: Server, list_tools_handler, list_resources_handler) -> str:
    """Generates DXT markdown from server definition."""
    tools = await list_tools_handler()
    resources = await list_resources_handler()

    markdown = """# DXT for MVG Störung MCP Server

This document provides the Developer Experience Toolkit (DXT) for the MVG Störung MCP Server.

## Overview

The MVG Störung MCP Server provides real-time, cached access to Munich Public Transport (MVG) disruption data.

## MCP Client Configuration

To connect your MCP client to this server, use the following configuration:

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

---
"""

    # Add Tools
    markdown += "\n## Available Tools\n\n"
    for tool in tools:
        markdown += f"### `{tool.name}`\n\n"
        markdown += f"{tool.description}\n\n"
        if tool.inputSchema:
            markdown += "**Input Schema:**\n\n"
            markdown += f"```json\n{json.dumps(tool.inputSchema, indent=2)}\n```\n\n"
        
        example_args = {}
        if tool.inputSchema and tool.inputSchema.get('properties'):
            for prop, schema in tool.inputSchema['properties'].items():
                if schema.get('default') is not None:
                    example_args[prop] = schema.get('default')
                elif 'string' in schema.get('type', ''):
                    if prop == 'query':
                        example_args[prop] = "störung"
                    elif prop == 'line':
                        example_args[prop] = "U6"
                    else:
                        example_args[prop] = "example"
                elif 'boolean' in schema.get('type', ''):
                    example_args[prop] = False
        
        # specific example for search_incidents
        if tool.name == 'search_incidents':
            example_args = {"query": "Aufzug", "line": "U3"}


        markdown += "**Example Call:**\n\n"
        markdown += f'```json\n{{\n  "method": "tools/call",\n  "params": {{\n    "name": "{tool.name}",\n    "arguments": {json.dumps(example_args)}\n  }}\n}}\n```\n\n'
        markdown += "\n---\n"


    # Add Resources
    markdown += "\n## Available Resources\n\n"
    for resource in resources:
        markdown += f"### `{resource.uri}`\n\n"
        markdown += f"**Name:** {resource.name}\n\n"
        markdown += f"**Description:** {resource.description}\n\n"
        markdown += f"**MIME Type:** {resource.mimeType}\n\n"
        markdown += "**Example Read:**\n\n"
        markdown += f'```json\n{{\n  "method": "resources/read",\n  "params": {{\n    "uri": "{resource.uri}"\n  }}\n}}\n```\n\n'
        markdown += "\n---\n"
        
    return markdown

