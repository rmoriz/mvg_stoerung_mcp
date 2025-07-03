#!/bin/bash
# Start script for MVG MCP Server

echo "Starting MVG MCP Server..."
echo "=========================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import httpx, pydantic" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install httpx pydantic
fi

# Try to install MCP if not available
if ! python -c "import mcp" 2>/dev/null; then
    echo "Warning: MCP package not found. Installing from pip..."
    pip install mcp || echo "Note: MCP package installation failed. You may need to install it manually."
fi

echo "Starting MCP server..."
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 mvg_mcp_server.py