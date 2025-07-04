import asyncio
import os
import shutil
import zipfile
import json
import subprocess
import sys
from pathlib import Path

async def download_dependencies(lib_dir: str, requirements_file: str = "requirements.txt"):
    """Download Python dependencies to lib/ directory using pip"""
    print("Downloading Python dependencies...")
    
    # Create lib directory
    os.makedirs(lib_dir, exist_ok=True)
    
    # Read requirements
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"Dependencies to download: {requirements}")
    
    # Download each package to lib directory (WITH dependencies to get anyio, etc.)
    for requirement in requirements:
        print(f"Downloading {requirement}...")
        try:
            # Install package files for direct import (including transitive dependencies)
            subprocess.run([
                sys.executable, "-m", "pip", "install",
                "--target", lib_dir,
                requirement
            ], capture_output=True, text=True, check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to download {requirement}: {e}")
    
    print("Dependencies downloaded to lib/ (including transitive dependencies)")

def create_bootstrap_script(temp_dir: str):
    """Create a bootstrap script that sets up the Python path"""
    bootstrap_content = '''#!/usr/bin/env python3
"""
Bootstrap script for MVG MCP Server
Sets up Python path to include bundled libraries
"""
import sys
import os
from pathlib import Path

# Add lib directory to Python path
script_dir = Path(__file__).parent
lib_dir = script_dir / "lib"
if lib_dir.exists():
    sys.path.insert(0, str(lib_dir))

# Import and run the main server
try:
    from mvg_mcp_server import main
    import asyncio
    asyncio.run(main())
except ImportError as e:
    print(f"Error importing mvg_mcp_server: {e}")
    print("Make sure all dependencies are properly bundled in lib/")
    sys.exit(1)
'''
    
    bootstrap_path = os.path.join(temp_dir, "server", "bootstrap.py")
    with open(bootstrap_path, "w", encoding='utf-8') as f:
        f.write(bootstrap_content)
    
    # Make it executable
    os.chmod(bootstrap_path, 0o755)
    print("Created bootstrap script")

async def main():
    """Generates a refactored DXT extension with bundled libraries in lib/"""
    # Create temporary directory
    temp_dir = "tmp_dxt_package"
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(f"{temp_dir}/server", exist_ok=True)
    os.makedirs(f"{temp_dir}/server/lib", exist_ok=True)
    
    try:
        print("Generating refactored DXT package...")
        
        # Download dependencies to lib/ (including transitive dependencies like anyio)
        await download_dependencies(f"{temp_dir}/server/lib")
        
        # Create bootstrap script
        create_bootstrap_script(temp_dir)
        
        # Define tools and resources statically
        tools = [
            {
                "name": "get_mvg_incidents",
                "description": "Get current MVG incidents (cached for 10+ minutes)"
            },
            {
                "name": "get_cache_status", 
                "description": "Get information about the cache status"
            },
            {
                "name": "search_incidents",
                "description": "Search incidents by line, title, or description"
            }
        ]
        
        # Create manifest.json
        manifest = {
            "dxt_version": "0.1",
            "name": "mvg-stoerung-mcp",
            "display_name": "MVG Stoerung MCP Server",
            "version": "1.1.0",
            "description": "Munich Public Transport (MVG) disruption data MCP server with intelligent caching",
            "long_description": "This extension provides cached access to Munich Public Transport (MVG) disruption data through an MCP server. It implements intelligent 10+ minute caching, search functionality, and real-time incident monitoring for the Munich transit system. This version includes bundled dependencies for easier deployment.",
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
                "entry_point": "server/bootstrap.py",
                "mcp_config": {
                    "command": "python3",
                    "args": ["${__dirname}/server/bootstrap.py"],
                    "env": {
                        "PYTHONPATH": "${__dirname}/server/lib:${__dirname}/server"
                    }
                }
            },
            "tools": tools,
            "keywords": ["mvg", "munich", "transport", "public-transport", "incidents", "disruption", "mcp"],
            "license": "CC0-1.0",
            "compatibility": {
                "claude_desktop": ">=0.10.0",
                "platforms": ["darwin", "win32", "linux"],
                "runtimes": {
                    "python": ">=3.8.0 <4"
                }
            },
            "bundle_info": {
                "type": "self-contained",
                "dependencies_location": "server/lib/",
                "venv_included": False,
                "bootstrap_script": "server/bootstrap.py"
            }
        }
        
        # Write manifest.json
        print("Creating manifest.json...")
        with open(f"{temp_dir}/manifest.json", "w", encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # Copy server files
        print("Copying server files...")
        shutil.copy2("mvg_mcp_server.py", f"{temp_dir}/server/")
        
        # Create requirements reference
        with open(f"{temp_dir}/server/requirements.txt", "w", encoding='utf-8') as f:
            f.write("# Dependencies are bundled in lib/ directory\n")
            f.write("# Original requirements:\n")
            with open("requirements.txt", "r") as orig:
                for line in orig:
                    f.write(f"# {line}")
        
        # Create README
        readme_content = f"""# {manifest['display_name']}

{manifest['long_description']}

## Quick Start

This DXT package includes all dependencies bundled in the `lib/` directory.

### Installation
1. Download the `.dxt` file
2. Open with Claude Desktop
3. The extension will be automatically configured

## Tools Available

"""
        for tool in tools:
            readme_content += f"### {tool['name']}\n{tool['description']}\n\n"
        
        readme_content += """## Bundle Information

This package uses a refactored bundling approach:
- Dependencies bundled in `server/lib/` directory (including transitive dependencies like anyio)
- No virtual environment included (smaller package size)
- Bootstrap script handles Python path setup automatically

## Technical Details

- Runtime: Python 3.8+
- Protocol: Model Context Protocol (MCP)
- Dependencies: httpx, pydantic, mcp, anyio (all bundled)

## Disclaimer

This project is not an official MVG project, not endorsed or recommended. Please ask MVG for permission prior to using it.
"""
        
        with open(f"{temp_dir}/README.md", "w", encoding='utf-8') as f:
            f.write(readme_content)
        
        # Create zip archive
        print("Creating DXT archive...")
        with zipfile.ZipFile("mvg_stoerung_mcp.dxt", "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                dirs[:] = [d for d in dirs if d != 'venv' and not d.startswith('.venv')]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    
                    if 'venv' in arcname or '.venv' in arcname:
                        continue
                    
                    zinfo = zipfile.ZipInfo(arcname)
                    zinfo.compress_type = zipfile.ZIP_DEFLATED
                    
                    if (arcname.endswith('.py') and 'bootstrap' in arcname):
                        zinfo.external_attr = 0o755 << 16
                    else:
                        zinfo.external_attr = 0o644 << 16
                    
                    with open(file_path, 'rb') as src:
                        zipf.writestr(zinfo, src.read())
        
        print("\nmvg_stoerung_mcp.dxt generated successfully!")
        print("\nPackage Contents:")
        print("- manifest.json (DXT specification)")
        print("- README.md (documentation)")
        print("- server/mvg_mcp_server.py (main MCP server)")
        print("- server/bootstrap.py (Python path setup)")
        print("- server/requirements.txt (reference)")
        print("- server/lib/ (bundled Python dependencies + transitive deps)")
        print("\nKey Improvements:")
        print("- Dependencies bundled in lib/ (no venv)")
        print("- Includes transitive dependencies (anyio, etc.)")
        print("- Automatic Python path setup")
        print("- Smaller package size")
        
        if os.path.exists("mvg_stoerung_mcp.dxt"):
            size_mb = os.path.getsize("mvg_stoerung_mcp.dxt") / (1024 * 1024)
            print(f"\nPackage size: {size_mb:.2f} MB")
        
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\nCleaned up temporary directory: {temp_dir}")

if __name__ == "__main__":
    asyncio.run(main())