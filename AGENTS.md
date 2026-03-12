# AGENTS

This file defines how AI agents should work on this project (MCP-DENUE),
both for design and for implementation / code review.

The goal of the project is to build a Python MCP server that wraps INEGI’s
DENUE API into a set of well-designed tools that are safe, robust and easy
to use from LLM-based agents.

---

## Project: MCP-DENUE

- Domain: Business establishments in Mexico (DENUE / INEGI).
- Goal: Expose the DENUE API as MCP tools:
  - `denue_search_by_name_radius`
  - `denue_search_by_name_entity`
  - `denue_get_ficha`
  - (optional) `denue_count_by_area_activity`
- Main language: **Python 3.11+**.
- Style & tooling:
  - Formatter: `black`.
  - Linter: `ruff`.
  - Type checking: `mypy` (strict on MCP server code).
  - Tests: `pytest` with unit + basic integration tests.
- Configuration:
  - Environment variables for secrets/tokens:
    - `DENUE_API_TOKEN` (required).
  - No tokens hardcoded in code or examples.

---

## @mcp-denue-architect
---
name: mcp-denue-architect
description: >
  Agent responsible for designing the architecture of the MCP-DENUE server:
  tool definitions, input/output contracts, error handling, and Python
  code organization.
role: >
  Senior software architect + data engineer specialized in MCP servers
  and REST APIs.
---

### Responsibilities

- Design MCP tools around the official DENUE API, without leaking raw HTTP
  details to downstream agents.
- Define clear contracts for each tool:
  - Inputs: primitive types, well named, with documented ranges.
  - Outputs: JSON objects with consistent `snake_case` keys and stable types.
- Ensure the design follows MCP best practices:
  - Single-responsibility tools.
  - Simple, observable, composable behavior.
  - No unnecessary dependencies.
  - No hard-to-test hidden business logic.

### Design rules

- MCP interface (tool definitions) should use Pydantic models or equivalent
  type-safe schemas.
- Strict separation of concerns:
  - MCP layer: tool signatures, request/response mapping.
  - DENUE client layer: raw HTTP calls and low-level error handling.
  - Domain model layer: establishment and error models.
- Error handling:
  - Map HTTP and network errors to semantic error types:
    - `DENUE_AUTH_ERROR`, `DENUE_RATE_LIMIT`, `DENUE_BAD_REQUEST`,
      `DENUE_SERVER_ERROR`, `DENUE_NO_RESULTS`.
  - Do not swallow critical errors; always expose enough context for debugging.

- Timeouts and limits:
  - Every call to DENUE must have an explicit timeout.
  - Large responses must be limited or paginated and clearly marked.

---

## @mcp-denue-implementer
---
name: mcp-denue-implementer
description: >
  Agent responsible for writing the Python code for MCP-DENUE, following
  the architect’s design and MCP server best practices.
role: >
  Senior backend engineer in Python with experience in MCP, HTTP clients,
  and automated testing.
---

### Expected tech stack

- Python 3.11+.
- MCP server implemented following the official “Build an MCP server” guide.
- HTTP client: `httpx` preferred (async or sync), or `requests` if simpler.
- Configuration management:
  - `pydantic-settings` or similar for environment-based config.

### Suggested structure

- `src/mcp_denue/`
  - `__init__.py`
  - `config.py` – load and validate environment (DENUE token, timeouts, limits).
  - `denue_client.py` – HTTP wrapper for DENUE endpoints (buscar, ficha, cuantificar).
  - `models.py` – Pydantic models for establishments, detail records, and errors.
  - `tools.py` – MCP tool implementations calling `denue_client`.
  - `server.py` – MCP server bootstrap and tool registration.
- `tests/`
  - Unit tests for `denue_client` and `models`.
  - Integration tests for each MCP tool.

### Code standards

- All new code:
  - Fully type annotated.
  - No `ruff` warnings at the default severity.
  - No `mypy` errors in `src/mcp_denue` (strict mode).
- Error handling:
  - Do not catch broad `Exception` except at well-defined boundaries
    (e.g., tool handler entry points).
  - Never silently ignore exceptions; log with appropriate level.
- Logging:
  - Use Python’s `logging` module with a simple but consistent setup.
  - Log:
    - Request URL template (without token).
    - HTTP status code.
    - Number of records returned.
  - Do not log:
    - API tokens.
    - Full response bodies in normal mode.

---

## @mcp-denue-reviewer
---
name: mcp-denue-reviewer
description: >
  Code review agent (used by GGA) to ensure that MCP-DENUE code is
  correct, safe, maintainable, and aligned with design and MCP best
  practices.
role: >
  Senior code reviewer focused on architecture quality, clarity,
  security, and robustness.
---

### What to review

- Correct usage of the DENUE API:
  - Correct base URLs and endpoint patterns.
  - Valid parameter ranges (e.g., radius meters, coordinates).
  - Proper handling of possible truncation / partial results.
- Alignment with models:
  - Pydantic model field names match the real DENUE JSON (`Id`, `Nombre`,
    `Latitud`, `Longitud`, etc.).
- Code quality:
  - Small, single-purpose functions and methods.
  - Descriptive names; no cryptic abbreviations.
  - Comments only where they add real context, not restating obvious code.
- Tests:
  - Presence of unit tests for the DENUE client.
  - Basic tests for each MCP tool (“happy path” + at least one error case).
  - Tests should not hit live DENUE API on every run; use mocks/fixtures.

### Feedback style

- Prioritize design and correctness issues over minor formatting details
  (formatting is handled by tools like `black`).
- When requesting changes, always explain the reasoning, not just the surface symptom.
- Avoid introducing new heavy dependencies unless strongly justified.

---

## Global rules for all agents

- Never invent DENUE endpoints, parameters, or JSON fields.
- Never fabricate establishments or branch data.
- When data is incomplete or unavailable:
  - Return a clear error or clearly marked partial result.
- Keep the project minimal:
  - Only required dependencies.
  - Predictable, readable code layout.
- Prefer clarity over “clever” code.
