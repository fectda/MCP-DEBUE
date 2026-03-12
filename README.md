# MCP-DENUE

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that provides AI agents (such as Claude Desktop, Cursor, etc.) access to INEGI's DENUE API. It allows searching and counting economic units (commercial establishments) in Mexico in a structured way.

## Requirements
- An INEGI DENUE API key. You can get one at the [official INEGI portal](https://www.inegi.org.mx/servicios/api_denue.html).
- Docker installed on your system.

## Installation and Usage

The easiest and most reliable way to use this MCP server is via Docker. The image is automatically built and hosted on GitHub Container Registry (GHCR), meaning you don't need to clone the repository, install Python, or manage virtual environments.

**Configure your MCP Client (e.g., Claude Desktop or Cursor):**

Add the following configuration to your client's settings file (e.g., `claude_desktop_config.json`). This tells your client to download and run the Docker container directly from GitHub.

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
        "ghcr.io/fectda/mcp-debue:latest"
      ]
    }
  }
}
```
*(Docker will automatically download the image the first time it runs).*

---

## Development and Testing (For contributors)
If you want to modify the code of this server locally:

1. Clone the repository:
```bash
git clone https://github.com/fectda/MCP-DEBUE.git
cd MCP-DEBUE
```

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
