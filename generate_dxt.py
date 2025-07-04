import asyncio
import os
import shutil
import zipfile
import json
from mvg_mcp_server import server, handle_list_tools, handle_list_resources

async def main():
    """Generates a proper DXT extension with manifest.json."""
    # Create temporary directory
    temp_dir = "tmp_dxt_package"
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(f"{temp_dir}/server", exist_ok=True)
    
    try:
        # Get tools and resources from the server
        tools = await handle_list_tools()
        resources = await handle_list_resources()
        
        # Create manifest.json
        manifest = {
            "dxt_version": "0.1",
            "name": "mvg-stoerung-mcp",
            "display_name": "MVG Stoerung MCP Server",
            "version": "1.0.0",
            "description": "Munich Public Transport (MVG) disruption data MCP server with intelligent caching",
            "long_description": "This extension provides cached access to Munich Public Transport (MVG) disruption data through an MCP server. It implements intelligent 10+ minute caching, search functionality, and real-time incident monitoring for the Munich transit system.",
            "author": {
                "name": "MVG Stoerung MCP",
                "url": "https://github.com/rmoriz/mvg_stoerung_mcp"
            },
            "repository": {
                "type": "git",
                "url": "https://github.com/rmoriz/mvg_stoerung_mcp"
            },
            "server": {
                "type": "python",
                "entry_point": "server/mvg_mcp_server.py",
                "mcp_config": {
                    "command": "python3",
                    "args": ["${__dirname}/server/mvg_mcp_server.py"],
                    "env": {
                        "PYTHONPATH": "${__dirname}/server"
                    }
                }
            },
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description
                } for tool in tools
            ],
            "keywords": ["mvg", "munich", "transport", "public-transport", "incidents", "disruption", "mcp"],
            "license": "CC0-1.0",
            "compatibility": {
                "claude_desktop": ">=0.10.0",
                "platforms": ["darwin", "win32", "linux"],
                "runtimes": {
                    "python": ">=3.8.0 <4"
                }
            }
        }
        
        # Write manifest.json
        with open(f"{temp_dir}/manifest.json", "w", encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # Copy server files
        shutil.copy2("mvg_mcp_server.py", f"{temp_dir}/server/")
        shutil.copy2("requirements.txt", f"{temp_dir}/server/")
        
        # Create a simple README
        readme_content = f"""# {manifest['display_name']}

{manifest['long_description']}

## Tools Available

"""
        for tool in tools:
            readme_content += f"- **{tool.name}**: {tool.description}\n"
        
        readme_content += f"""
## Resources Available

"""
        for resource in resources:
            readme_content += f"- **{resource.uri}**: {resource.description}\n"
        
        readme_content += """
## Installation

This is a Desktop Extension (DXT) for Claude Desktop and other MCP-compatible applications.

1. Download the .dxt file
2. Open it with Claude Desktop to install
3. The extension will be automatically configured

## Data Source

- API: https://www.mvg.de/api/bgw-pt/v3/messages
- Caching: 10+ minutes intelligent caching
- Provider: Munich Public Transport (MVG)

## Disclaimer

This project is not an official MVG project, not endorsed or recommended. Please ask MVG for permission prior to using it.
"""
        
        with open(f"{temp_dir}/README.md", "w", encoding='utf-8') as f:
            f.write(readme_content)
        
        # Create zip archive
        with zipfile.ZipFile("mvg_stoerung_mcp.dxt", "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        print("mvg_stoerung_mcp.dxt generated successfully as proper DXT extension.")
        print("Contents:")
        print("- manifest.json (DXT specification)")
        print("- server/mvg_mcp_server.py (MCP server)")
        print("- server/requirements.txt (dependencies)")
        print("- README.md (documentation)")
        
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    asyncio.run(main())