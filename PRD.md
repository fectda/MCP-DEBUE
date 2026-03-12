# PRD for MCP-DENUE (MCP server on top of INEGI’s DENUE API)

## 1. Context and goal

INEGI’s DENUE API exposes identification, location, economic activity and size data for more than five million business establishments in Mexico, queryable by state, municipality and spatial filters through a REST API secured with a token. The goal of this PRD is to define the requirements for an MCP (Model Context Protocol) server called **MCP-DENUE** that allows AI agents to query these establishments in a structured, agent‑friendly way, with a primary use case of locating physical branches of consumer brands in Mexico.

MCP-DENUE will be one of the main data sources for a “brand stores in Mexico” agent, and will be composed with other MCP servers such as OpenStreetMap MCP for geospatial enrichment and validation.

## 2. Target users and use cases

### 2.1 Target users

- Developers building AI agents (LLM-based) that need authoritative business location data for Mexico.
- Data engineers and analysts who want to enrich their pipelines with official INEGI establishment data.
- Orchestrator agents that must find brand branches in Mexico as part of larger workflows.

### 2.2 Primary use cases

1. **Search brand branches within a radius**  
   Given a `brand_name`, a coordinate pair (`lat`, `lon`) and a radius in meters, return all establishments whose name or legal name matches or contains the brand name, using DENUE’s `buscar` method.

2. **Search brand branches by state/municipality**  
   Given a `brand_name`, state and optionally municipality, return all establishments whose name or legal name matches or contains the brand name, using DENUE methods that filter by state/entity and area.

3. **Get detailed record (“ficha”) for a specific establishment**  
   Given an establishment identifier (Id) or CLEE key, return the complete detailed record, including full address, activity, size, contact data, and coordinates, using DENUE’s `Ficha` endpoint.

4. **Count establishments for coverage validation**  
   Given a geographic area and economic activity filter, return the total number of establishments using the `Cuantificar` endpoint, to help validate and diagnose coverage.

## 3. Data source description (DENUE API)

DENUE’s API is served under `https://www.inegi.org.mx/app/api/denue/v1/consulta/` and is invoked by passing parameters directly in the URL, including search text (`#condicion`), coordinates, search radius and the API token. The documentation specifies logical methods such as `Buscar`, `Nombre`, `BuscarEntidad`, `BuscarAreaAct`, `Ficha` and `Cuantificar`, each with its own URL pattern and parameters.

Responses are JSON arrays of establishments that include structured fields such as `Id`, `Nombre`, `Razon_social`, `Clase_actividad`, `Estrato`, `Tipo_vialidad`, `Calle`, `Num_Exterior`, `Num_Interior`, `Colonia`, `CP`, `Ubicacion`, `Telefono`, `Correo_e`, `Sitio_internet`, `Tipo`, `Latitud`, `Longitud`, `CentroComercial`, `TipoCentroComercial`, and `NumLocal`.

## 4. Functional scope of MCP-DENUE

### 4.1 Scope objective

The MCP server must expose a small, well‑designed set of tools that wrap DENUE’s API in LLM‑friendly contracts, hiding HTTP details and raw URL templates while mapping to the documented endpoints. The tools should cover:

- Search by name and radius.
- Search by name and state/municipality.
- Fetch detailed record (“ficha”) of an establishment.
- Count establishments by area/activity (optional but recommended).

### 4.2 Proposed MCP tools

#### 4.2.1 `denue_search_by_name_radius`

- **Description**: Search establishments whose name or legal name matches or contains a search string within a radius (in meters) around a given point (`lat`, `lon`), backed by DENUE’s `Buscar` endpoint.
- **Input parameters**:
  - `brand_name: string` – Free text search, mapped to `#condicion`.
  - `lat: number` – Latitude in decimal degrees.
  - `lon: number` – Longitude in decimal degrees.
  - `radius_m: number` – Search radius in meters (must respect API maximums).
  - Optional: `max_results: number` – Soft limit for number of records returned by this tool.
- **Output**: List of `Establishment` objects with at least:
  - `clee: string | null`
  - `id: string`
  - `name: string`
  - `legal_name: string | null`
  - `activity_class: string`
  - `size_class: string`
  - `street_type: string`
  - `street_name: string`
  - `ext_number: string | null`
  - `int_number: string | null`
  - `neighborhood: string | null`
  - `postal_code: string | null`
  - `location: string` (combined locality, municipality, state string).
  - `phone: string | null`
  - `email: string | null`
  - : string | null`
  - `unit_type: string`
  - `latitude: number`
  - `longitude: number`
  - `shopping_center: string | null`
  - `shopping_center_type: string | null`
  - `unit_number: string | null`
- **Additional behavior**:
  - If the API returns more records than the server is allowed to return in one call, either:
    - Truncate to `max_results` and mark the response as truncated, or
    - Provide a simple pagination mechanism (cursor or page index).

#### 4.2.2 `denue_search_by_name_entity`

- **Description**: Search establishments by name/brand within a given state and optionally municipality, using DENUE’s entity/area search endpoints.
- **Input parameters**:
  - `brand_name: string`
  - `state_code: string` – INEGI state code is preferred.
  - `municipality_code: string | null` – Optional municipality code.
  - Optional: `max_results: number`.
- **Output**: Same `Establishment` schema as `denue_search_by_name_radius`.
- **Additional behavior**:
  - If DENUE truncates or limits the number of records, surface this fact in the response (e.g., `truncated: true`).

#### 4.2.3 `denue_get_ficha`

- **Description**: Fetch a detailed record (“ficha”) for a single establishment using its `Id` or CLEE key, backed by DENUE’s `Ficha` endpoint.
- **Input parameters**:
  - `id: string` – Establishment Id or CLEE (following what the endpoint expects).
- **Output**: `EstablishmentDetail` object, with all fields provided by `Ficha`, mirroring DENUE’s response as closely as possible.

#### 4.2.4 `denue_count_by_area_activity` (optional)

- **Description**: Use the `Cuantificar` endpoint to get the total number of establishments for a given geographic area and economic activity, to be used mainly for validation and analytics.
- **Input parameters**:
  - `area_code: string`
  - `activity_id: string | null`
  - `size_class: string | null`
- **Output**:
  - `activity_id: string`
  - `area_code: string`
  - `total_establishments: number`

## 5. Non‑functional requirements

### 5.1 Authentication and configuration

- MCP-DENUE must read the DENUE API token from environment variables (e.g. `DENUE_API_TOKEN`).
- Tokens must never be logged or leaked in error messages.
- Missing token should be surfaced as a clear configuration error.

### 5.2 Performance and API limits

- Implement reasonable request timeouts for all HTTP calls to DENUE.
- Respect any documented or inferred rate limits by:
  - Configurable request throttling (requests per second).
  - Backoff or clear errors on rate‑limit responses, categorized as `DENUE_RATE_LIMIT`.
- For high‑volume queries, tools must allow limiting or paging through results.

### 5.3 Error handling

Errors must be mapped to semantic categories so that LLM agents can reason about them:

- `DENUE_AUTH_ERROR` – missing or invalid token.
- `DENUE_RATE_LIMIT` – rate limit exceeded.
- `DENUE_BAD_REQUEST` – invalid parameters, out‑of‑range radius, malformed location, etc.
- `DENUE_SERVER_ERROR` – 5xx errors or upstream service failures.
- `DENUE_NO_RESULTS` – valid query, but no establishments found.

Responses must include:

- A human‑readable message.
- Optional hints (e.g. “try reducing the radius”, “try specifying municipality”).

### 5.4 Data format and normalization

- All JSON keys returned by MCP-DENUE should follow `snake_case`.
- Field names must be clearly documented and mapped from DENUE’s original names.
- Numeric fields such as `latitude` and `longitude` must be exposed as floats.
- The server must not “correct” data values from DENUE; only normalize naming and types.

### 5.5 Logging and observability

- Log (at info/debug level):
  - Endpoint template used (without token).
  - HTTP status code.
  - Number of records returned.
- Avoid logging full response bodies in normal mode to keep logs small.
- Consider including simple health and readiness checks if deploying to production, following MCP server deployment best practices.

## 6. Interaction with LLM agents and other MCP servers

### 6.1 Typical usage pattern in agents

A typical “brand stores in Mexico” agent will:

1. Interpret a user request like “all Cuidado con el Perro stores in CDMX”.
2. Convert the location into either:
   - A state/municipality pair, or
   - One or more coordinates (possibly by using an OpenStreetMap MCP geocoder).
3. Call `denue_search_by_name_entity` or `denue_search_by_name_radius` as appropriate.
4. Optionally call `denue_get_ficha` for specific establishments to enrich details.
5. Optionally cross‑validate coordinates and addresses with an OSM MCP server.

### 6.2 Compatibility with OpenStreetMap MCP

- MCP-DENUE outputs must be easy to pass into OSM MCP tools for:
  - Geocoding / reverse geocoding.
  - Nearby POI lookup.
  - Neighborhood/context analysis.

## 7. Security and compliance

- Respect INEGI’s DENUE terms of use and open data policies, including any specific constraints documented for the API.
- MCP-DENUE is strictly read‑only; it must not support any write operations.
- Any future integration with additional INEGI APIs must keep these guarantees and extend configuration without breaking backward compatibility.

## 8. Deliverables

- MCP-DENUE server source code (Python), including:
  - Tool implementations as described above.
  - Configuration, logging and error handling per this PRD.
- Documentation:
  - How to run the server.
  - How to configure `DENUE_API_TOKEN`.
  - Example tool calls and responses.
- Tests:
  - Unit tests for DENUE HTTP client and models.
  - Integration tests for each MCP tool with at least “happy path” and common error cases.

## 9. Risks and open questions

- **Brand coverage**: Some brands may not be captured in DENUE with exactly the same commercial name as used publicly (differences between trade name and legal name), leading to imperfect text matching.
- **API limits**: If rate limits or maximum response sizes are stricter than expected, the server might need more sophisticated pagination or caching mechanisms.
- **Geographic normalization**: Robust handling of state and municipality codes might require additional INEGI catalogs or a separate MCP for geographic catalogs.


## Useful links

- INEGI DENUE API documentation (official):
  - https://www.inegi.org.mx/servicios/api_denue.html
- DENUE methodology / data dictionary (PDF):
  - https://www.snieg.mx/DocAcervoINN/documentacion/inf_nvo_acervo/SNIE/CE2014/DENUE_20181A_Metodologia.pdf
- MCP server official build guide:
  - https://modelcontextprotocol.io/docs/develop/build-server
- MCP best practices (architecture & implementation):
  - https://mcp-best-practice.github.io/mcp-best-practice/
- OpenStreetMap MCP server examples (for geospatial composition):
  - https://github.com/NERVsystems/osmmcp
  - https://github.com/jagan-shanmugam/open-streetmap-mcp
