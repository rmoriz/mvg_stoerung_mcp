import pytest
import respx
from httpx import Response

from mvg_mcp_server import MVGDataFetcher

@pytest.fixture
def mock_mvg_api():
    with respx.mock(base_url=MVGDataFetcher.MVG_API_URL) as mock:
        mock.get("/").respond(200, json=[
            {
                "type": "INCIDENT",
                "title": "U-Bahn Störung",
                "description": "Signalstörung auf der U3",
                "lines": [{"label": "U3"}],
            },
            {
                "type": "INFO",
                "title": "Bauarbeiten",
                "description": "Informationen zu Bauarbeiten",
            }
        ])
        yield mock
