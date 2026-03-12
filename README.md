# MCP-DENUE

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that provides AI agents (such as Claude Desktop, Cursor, etc.) access to INEGI's DENUE API. It allows searching and counting economic units (commercial establishments) in Mexico in a structured way.

## Requirements
- An INEGI DENUE API key. You can get one at the [official INEGI portal](https://www.inegi.org.mx/servicios/api_denue.html).
- Python 3.11+ or Docker.

## Installation and Usage (For end users)

### Option 1: Standard Python (No extra tools required)
If you just want to use standard Python, clone the repository, install it, and run it directly. This is the most universal way.

1. Clone and install:
```bash
git clone https://github.com/fectda/MCP-DEBUE.git
cd MCP-DEBUE
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install .
```

2. Add this configuration to your MCP client (e.g., `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "mcp-denue": {
      "command": "/absolute/path/to/MCP-DEBUE/.venv/bin/mcp-denue",
      "env": {
        "DENUE_API_TOKEN": "YOUR_INEGI_TOKEN_HERE"
      }
    }
  }
}
```

### Option 2: Using `uvx` (Fastest, no cloning required)
Anthropic (creators of MCP) recommend [uv](https://docs.astral.sh/uv/) as the industry standard to run Python MCP servers without manually creating virtual environments (it works exactly like `npx` does for Node.js).

If you have `uv` installed, add this to your MCP client:
```json
{
  "mcpServers": {
    "mcp-denue": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/fectda/MCP-DEBUE.git",
        "mcp-denue"
      ],
      "env": {
        "DENUE_API_TOKEN": "YOUR_INEGI_TOKEN_HERE"
      }
    }
  }
}
```

### Option 3: Using Docker
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
        "fectda/MCP-DEBUE"
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
