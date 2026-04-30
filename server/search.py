from typing import Any
import fastmcp as FastMCP
import httpx

mcp = FastMCP("weather")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "Weather-app-1.0.1"

@mcp.tool()
async def get_weather(url: str) -> dict[str, Any] | None:
    """Get the weather for a given location"""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            mcp.logger.error(f"HTTP error: {e}")
            return None
        except Exception as e:
            mcp.logger.error(f"Error: {e}")
            return None