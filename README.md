# MVG Störung MCP Server

A Model Context Protocol (MCP) server that provides cached access to Munich Public Transport (MVG) disruption data.

![grafik](https://github.com/user-attachments/assets/266d6068-b29c-4abe-8306-3e2e5f91445c)

## Features

- **Cached Data**: Automatically caches MVG incident data for at least 10 minutes to reduce API calls
- **Real-time Incidents**: Fetches current incidents from the official MVG API
- **Search Functionality**: Search incidents by line, title, or description
- **Enhanced Data**: Adds human-readable timestamps and formats data for easy consumption
- **MCP Compatible**: Works with any MCP-compatible client

## Data Source

This server uses the official MVG API endpoint: `https://www.mvg.de/api/bgw-pt/v3/messages`

The server filters the API response to only return incidents (type=INCIDENT) and enhances the data with:
- Human-readable timestamps
- Formatted descriptions
- Deduplicated line information

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

## Usage

### Running the Server

```bash
python mvg_mcp_server.py
```

### Available Tools

1. **get_mvg_incidents**: Get current MVG incidents (cached for 10+ minutes)
   - Optional parameter: `force_refresh` (boolean) - Force refresh cache even if not expired

2. **get_cache_status**: Get information about the cache status

3. **search_incidents**: Search incidents by line, title, or description
   - Required parameter: `query` (string) - Search query
   - Optional parameter: `line` (string) - Filter by specific line (e.g., 'U6', 'S1')

### Available Resources

1. **mvg://incidents**: Current incidents from Munich Public Transport (MVG)
2. **mvg://cache-info**: Information about the current cache status

## Example Usage

### Get All Current Incidents
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_mvg_incidents"
  }
}
```

### Search for U6 Line Issues
```json
{
  "method": "tools/call",
  "params": {
    "name": "search_incidents",
    "arguments": {
      "query": "verspätung",
      "line": "U6"
    }
  }
}
```

### Force Cache Refresh
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_mvg_incidents",
    "arguments": {
      "force_refresh": true
    }
  }
}
```

## Cache Behavior

- **Cache Duration**: 10 minutes minimum (configurable)
- **Automatic Refresh**: Cache is automatically refreshed when expired
- **Force Refresh**: Can be manually triggered via the `force_refresh` parameter
- **Cache Info**: View cache status including expiration time and cached item count

## Data Format

Each incident includes:
- `title`: Incident title
- `description`: Detailed description
- `type`: Always "INCIDENT"
- `publication`: Publication timestamp (Unix milliseconds)
- `publication_readable`: Human-readable publication time
- `validFrom`/`validTo`: Validity period
- `validFrom_readable`/`validTo_readable`: Human-readable validity times
- `lines`: Affected transport lines with details
- `provider`: Always "MVG"

## Error Handling

The server handles various error conditions:
- API timeouts and connection errors
- Invalid JSON responses
- Cache expiration
- Missing or malformed data

## Development

### Project Structure
```
├── mvg_mcp_server.py    # Main MCP server implementation
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Project configuration
└── README.md           # This file
```

### Dependencies
- `mcp>=1.0.0`: Model Context Protocol framework
- `httpx>=0.25.0`: Async HTTP client
- `pydantic>=2.0.0`: Data validation and serialization

## License

This project is dedicated to the public domain under the CC0 1.0 Universal license. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
