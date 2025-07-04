
import asyncio
from mvg_mcp_server import server, handle_list_tools, handle_list_resources
from dxt import generate_dxt_markdown

async def main():
    """Generates the DXT markdown file."""
    markdown = await generate_dxt_markdown(server, handle_list_tools, handle_list_resources)
    with open("DXT.md", "w") as f:
        f.write(markdown)
    print("DXT.md generated successfully.")

if __name__ == "__main__":
    asyncio.run(main())
