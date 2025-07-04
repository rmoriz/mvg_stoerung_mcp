
import asyncio
from mvg_mcp_server import server, handle_list_tools, handle_list_resources
from dxt import generate_dxt_file

async def main():
    """Generates the .dxt file."""
    # Generate .dxt file version
    dxt_content = await generate_dxt_file(server, handle_list_tools, handle_list_resources)
    with open("mvg_stoerung_mcp.dxt", "w") as f:
        f.write(dxt_content)
    print("mvg_stoerung_mcp.dxt generated successfully.")

if __name__ == "__main__":
    asyncio.run(main())
