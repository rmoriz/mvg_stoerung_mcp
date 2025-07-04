
import asyncio
import os
import shutil
import zipfile
from mvg_mcp_server import server, handle_list_tools, handle_list_resources
from dxt import generate_dxt_file

async def main():
    """Generates the .dxt file as a zip archive."""
    # Create temporary directory
    temp_dir = "tmp_dxt_package"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Generate .dxt content and save as README.md in temp directory
        dxt_content = await generate_dxt_file(server, handle_list_tools, handle_list_resources)
        with open(f"{temp_dir}/README.md", "w") as f:
            f.write(dxt_content)
        
        # Copy relevant project files
        files_to_include = [
            "mvg_mcp_server.py",
            "requirements.txt", 
            "mcp_config.json"
        ]
        
        for file in files_to_include:
            if os.path.exists(file):
                shutil.copy2(file, temp_dir)
        
        # Create zip archive
        with zipfile.ZipFile("mvg_stoerung_mcp.dxt", "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        print("mvg_stoerung_mcp.dxt generated successfully as zip archive.")
        
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    asyncio.run(main())
