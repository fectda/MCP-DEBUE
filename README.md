# MCP-DENUE

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that provides AI agents (such as Claude Desktop, Cursor, etc.) access to INEGI's DENUE API. It allows searching and counting economic units (commercial establishments) in Mexico in a structured way.

## Requirements
- An INEGI DENUE API key. You can get one at the [official INEGI portal](https://www.inegi.org.mx/servicios/api_denue.html).
- Python 3.11+ OR Docker installed on your system.

## Installation and Usage

You can connect this MCP server to your AI assistant using either a standard local Python environment (recommended for development and direct usage) or Docker (recommended if you don't want to install Python dependencies on your host machine).

### Option 1: Using a Local Python Environment (Standard)
This is the standard way to run an MCP server locally. You will clone the code, install it in a virtual environment, and point your MCP client to the generated executable.

**1. Clone the repository and install dependencies:**
```bash
git clone https://github.com/fectda/MCP-DEBUE.git
cd MCP-DEBUE

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install the project and its dependencies
pip install .
```

**2. Configure your MCP Client (e.g., Claude Desktop or Cursor):**
Add the following configuration to your client's settings file (e.g., `claude_desktop_config.json`). 

*Important: You must provide the absolute path to the `.venv/bin/mcp-denue` executable created in the previous step.*

```json
{
  "mcpServers": {
    "mcp-denue": {
      "command": "/ABSOLUTE/PATH/TO/MCP-DEBUE/.venv/bin/mcp-denue",
      "env": {
        "DENUE_API_TOKEN": "YOUR_INEGI_TOKEN_HERE"
      }
    }
  }
}
```

### Option 2: Using Docker (Isolated)
If you prefer not to manage Python versions or virtual environments, you can build a Docker image locally and run the server inside a container.

**1. Clone the repository and build the Docker image locally:**
```bash
git clone https://github.com/fectda/MCP-DEBUE.git
cd MCP-DEBUE

# Build the local image and name it 'mcp-denue'
docker build -t mcp-denue .
```

**2. Configure your MCP Client (e.g., Claude Desktop or Cursor):**
Add the following configuration to your client's settings file. This tells your client to spin up the Docker container we just built (`mcp-denue`) every time it needs the server.

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
        "mcp-denue"
      ]
    }
  }
}
```

## Development and Testing (For contributors)
If you want to modify the code of this server locally:

1. Follow "Option 1" to setup your local `.venv`.
2. Install the development tools instead of just the app:
```bash
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
