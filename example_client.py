#!/usr/bin/env python3
"""
Example client for testing the MVG MCP Server
This demonstrates how to interact with the server programmatically
"""

import asyncio
import json
import subprocess
import sys
from typing import Any, Dict


class MCPClient:
    """Simple MCP client for testing"""
    
    def __init__(self, server_command: str):
        self.server_command = server_command
        self.process = None
    
    async def start(self):
        """Start the MCP server process"""
        self.process = await asyncio.create_subprocess_exec(
            *self.server_command.split(),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server"""
        if not self.process:
            raise RuntimeError("Server not started")
        
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")
        
        return json.loads(response_line.decode())
    
    async def close(self):
        """Close the client and terminate server"""
        if self.process:
            self.process.terminate()
            await self.process.wait()


async def test_mcp_protocol():
    """Test the MCP protocol with the server"""
    print("Testing MCP Protocol...")
    
    client = MCPClient("python mvg_mcp_server.py")
    
    try:
        await client.start()
        
        # Test initialization
        print("1. Testing initialization...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await client.send_request(init_request)
        print(f"Init response: {response}")
        
        # Test listing tools
        print("\n2. Testing list tools...")
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = await client.send_request(list_tools_request)
        print(f"Tools: {[tool['name'] for tool in response.get('result', {}).get('tools', [])]}")
        
        # Test calling get_mvg_incidents tool
        print("\n3. Testing get_mvg_incidents tool...")
        call_tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_mvg_incidents",
                "arguments": {}
            }
        }
        
        response = await client.send_request(call_tool_request)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            data = json.loads(content)
            print(f"Retrieved {data['count']} incidents")
            print(f"Cache status: {data['cache_info']['status']}")
        
        # Test search tool
        print("\n4. Testing search_incidents tool...")
        search_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "search_incidents",
                "arguments": {
                    "query": "verspätung"
                }
            }
        }
        
        response = await client.send_request(search_request)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            data = json.loads(content)
            print(f"Search found {data['count']} incidents matching 'verspätung'")
        
        # Test cache status
        print("\n5. Testing get_cache_status tool...")
        cache_status_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "get_cache_status",
                "arguments": {}
            }
        }
        
        response = await client.send_request(cache_status_request)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            cache_info = json.loads(content)
            print(f"Cache status: {cache_info}")
        
        print("\n✓ MCP Protocol tests completed successfully!")
        
    except Exception as e:
        print(f"✗ MCP Protocol test failed: {e}")
        return False
    finally:
        await client.close()
    
    return True


async def main():
    """Run the example client"""
    print("MVG MCP Server - Example Client")
    print("=" * 40)
    
    success = await test_mcp_protocol()
    
    if success:
        print("\n🎉 All client tests passed!")
        return 0
    else:
        print("\n❌ Client tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))