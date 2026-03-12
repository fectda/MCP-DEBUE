import asyncio
import logging
import json
import sys
from typing import Any, Callable
from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult
from mcp.server.stdio import stdio_server

from .config import get_config
from .denue_client import DenueClient, DenueError
from .tools import ToolsWrapper

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Server("mcp-denue", version="0.1.0")


@app.list_tools()  # type: ignore
async def list_tools() -> list[Tool]:
    """List available DENUE tools."""
    return [
        Tool(
            name="denue_search_by_name_radius",
            description="Search establishments whose name or legal name matches or contains a search string within a radius (in meters) around a given point (lat, lon).",
            inputSchema={
                "type": "object",
                "properties": {
                    "brand_name": {"type": "string", "description": "Free text search"},
                    "lat": {
                        "type": "number",
                        "description": "Latitude in decimal degrees",
                    },
                    "lon": {
                        "type": "number",
                        "description": "Longitude in decimal degrees",
                    },
                    "radius_m": {
                        "type": "number",
                        "description": "Search radius in meters",
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Soft limit for number of records returned",
                    },
                },
                "required": ["brand_name", "lat", "lon", "radius_m"],
            },
        ),
        Tool(
            name="denue_search_by_name_entity",
            description="Search establishments by name/brand within a given state and optionally municipality.",
            inputSchema={
                "type": "object",
                "properties": {
                    "brand_name": {"type": "string", "description": "Free text search"},
                    "state_code": {"type": "string", "description": "INEGI state code"},
                    "municipality_code": {
                        "type": "string",
                        "description": "Optional INEGI municipality code",
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Soft limit for number of records returned",
                    },
                },
                "required": ["brand_name", "state_code"],
            },
        ),
        Tool(
            name="denue_get_ficha",
            description="Fetch a detailed record for a single establishment using its Id or CLEE key.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Establishment Id or CLEE"}
                },
                "required": ["id"],
            },
        ),
        Tool(
            name="denue_count_by_area_activity",
            description="Use the Cuantificar endpoint to get the total number of establishments for a given geographic area and economic activity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "area_code": {
                        "type": "string",
                        "description": "Geographic area code",
                    },
                    "activity_id": {
                        "type": "string",
                        "description": "Economic activity filter",
                    },
                    "size_class": {
                        "type": "string",
                        "description": "Size class filter",
                    },
                },
                "required": ["area_code"],
            },
        ),
        Tool(
            name="ping",
            description="Minimal ping tool to test server responsiveness",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


async def safe_call(func: Callable[..., Any], *args: Any, **kwargs: Any) -> CallToolResult:
    try:
        res = await func(*args, **kwargs)
        # Assuming Pydantic models with .model_dump()
        try:
            if hasattr(res, "model_dump_json"):
                json_text = res.model_dump_json()
            elif hasattr(res, "json"):
                json_text = res.json()
            else:
                json_text = json.dumps(res, default=str)
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            json_text = json.dumps({"error": "SERIALIZATION_ERROR", "message": str(e)})

        return CallToolResult(
            content=[TextContent(type="text", text=json_text)]
        )
    except DenueError as e:
        logger.error(f"DenueError in tool execution: {e.type} - {e.message}")
        return CallToolResult(
            isError=True,
            content=[
                TextContent(
                    type="text", text=json.dumps({"error": e.type, "message": str(e)})
                )
            ],
        )
    except Exception as e:
        logger.exception("Unexpected error in tool execution")
        return CallToolResult(
            isError=True,
            content=[
                TextContent(
                    type="text",
                    text=json.dumps({"error": "DENUE_SERVER_ERROR", "message": str(e)}),
                )
            ],
        )


@app.call_tool()  # type: ignore
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    if not hasattr(app, "wrapper"):
        return CallToolResult(
            isError=True,
            content=[
                TextContent(type="text", text="Server not initialized correctly.")
            ],
        )

    wrapper: ToolsWrapper = getattr(app, "wrapper")

    if name == "ping":
        return CallToolResult(content=[TextContent(type="text", text="pong")])
    elif name == "denue_search_by_name_radius":
        return await safe_call(
            wrapper.search_by_name_radius,
            arguments["brand_name"],
            arguments["lat"],
            arguments["lon"],
            arguments["radius_m"],
            arguments.get("max_results", 50),
        )
    elif name == "denue_search_by_name_entity":
        return await safe_call(
            wrapper.search_by_name_entity,
            arguments["brand_name"],
            arguments["state_code"],
            arguments.get("municipality_code"),
            arguments.get("max_results", 50),
        )
    elif name == "denue_get_ficha":
        return await safe_call(wrapper.get_ficha, arguments["id"])
    elif name == "denue_count_by_area_activity":
        return await safe_call(
            wrapper.count_by_area_activity,
            arguments["area_code"],
            arguments.get("activity_id"),
            arguments.get("size_class"),
        )
    else:
        return CallToolResult(
            isError=True,
            content=[TextContent(type="text", text=f"Unknown tool: {name}")],
        )


async def run() -> None:
    try:
        config = get_config()
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        logger.error(
            "Check if DENUE_API_TOKEN is set in your environment or in a .env file at the project root."
        )
        sys.exit(1)

    client = DenueClient(config)
    app.wrapper = ToolsWrapper(client)  # type: ignore

    async with stdio_server() as (read_stream, write_stream):
        logger.info("Starting MCP-DENUE server over stdio...")
        await app.run(read_stream, write_stream, app.create_initialization_options())

    await client.client.aclose()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
