# MCP-DENUE

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that provides AI agents (such as Claude Desktop, Cursor, etc.) access to INEGI's DENUE API. It allows searching and counting economic units (commercial establishments) in Mexico in a structured way.

## Requirements
- An INEGI DENUE API key. You can get one at the [official INEGI portal](https://www.inegi.org.mx/servicios/api_denue.html).
- `uv` installed (if using the Python option) or Docker.

## Installation and Usage (For end users)

### Option 1: Using `uvx` (Recommended, no cloning or dependency installation required)
If you have [uv](https://docs.astral.sh/uv/) installed, you can run this server directly from GitHub in any MCP client without worrying about virtual environments.

Add this configuration to your MCP client (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mcp-denue": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/your-username/mcp-denue.git",
        "mcp-denue"
      ],
      "env": {
        "DENUE_API_TOKEN": "YOUR_INEGI_TOKEN_HERE"
      }
    }
  }
}
```

### Option 2: Using Docker
*(If you wish to package it as a container, you can build and run this server via Docker, which isolates all dependencies).*

Add this configuration to your MCP client:

```json
{
  "mcpServers": {
    "mcp-denue": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "DENUE_API_TOKEN=YOUR_INEGI_TOKEN_HERE",
        "your-username/mcp-denue"
      ]
    }
  }
}
```

## Development and Testing (For contributors)
If you want to modify the code of this server locally:

1. Clone the repository.
2. Create a virtual environment and install development dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```
3. Run tests or linters:
```bash
pytest
ruff check .
mypy src
```

## Available Tools
- `denue_search_by_name_radius`: Searches for branches by name within a radius in meters from given coordinates.
- `denue_search_by_name_entity`: Searches for branches by name in a Mexican state and/or municipality.
- `denue_get_ficha`: Gets the full detailed record of an establishment by its ID.
- `denue_count_by_area_activity`: Counts the total number of establishments in an area by economic activity.
