import pytest
import respx
import json
import httpx
from mcp_denue.server import app, call_tool
from mcp_denue.config import Config
from mcp_denue.denue_client import DenueClient
from mcp_denue.tools import ToolsWrapper
from mcp.server import Server

@pytest.fixture
def mock_app() -> Server:
    config = Config(denue_api_token="TEST_TOKEN")
    client = DenueClient(config)
    setattr(app, "wrapper", ToolsWrapper(client))
    return app


@pytest.mark.asyncio
@respx.mock
async def test_call_tool_search_by_name_radius(mock_app: Server) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Buscar/oxxo/19.0,-99.0/500/TEST_TOKEN"
    respx.get(mock_url).mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "CLEE": "123",
                    "Id": "1",
                    "Nombre": "OXXO",
                    "Clase_actividad": "Minisuper",
                    "Estrato": "0 a 5 personas",
                    "Tipo_vialidad": "Calle",
                    "Calle": "Juarez",
                    "Ubicacion": "CDMX",
                    "Tipo": "Fijo",
                    "Latitud": "19.0",
                    "Clase_actividad": "Minisuper","Estrato": "0 a 5 personas","Tipo_vialidad": "Calle","Calle": "Juarez","Ubicacion": "CDMX","Tipo": "Fijo","Latitud": "19.0","Longitud": "-99.0",
                }
            ],
        )
    )

    result = await call_tool(
        "denue_search_by_name_radius",
        {"brand_name": "oxxo", "lat": 19.0, "lon": -99.0, "radius_m": 500},
    )

    assert not result.isError
    content = json.loads(result.content[0].text)
    assert len(content["results"]) == 1
    assert content["results"][0]["name"] == "OXXO"


@pytest.mark.asyncio
@respx.mock
async def test_call_tool_unknown(mock_app: Server) -> None:
    result = await call_tool("unknown_tool", {})
    assert result.isError
    assert "Unknown tool" in result.content[0].text

@pytest.mark.asyncio
@respx.mock
async def test_call_tool_search_by_name_entity(mock_app: Server) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}BuscarEntidad/oxxo/09/1/100/TEST_TOKEN"
    respx.get(mock_url).mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "CLEE": "123",
                    "Id": "1",
                    "Nombre": "OXXO",
                    "Latitud": "19.0",
                    "Clase_actividad": "Minisuper","Estrato": "0 a 5 personas","Tipo_vialidad": "Calle","Calle": "Juarez","Ubicacion": "CDMX","Tipo": "Fijo","Latitud": "19.0","Longitud": "-99.0",
                }
            ],
        )
    )

    result = await call_tool(
        "denue_search_by_name_entity",
        {"brand_name": "oxxo", "state_code": "09"},
    )
    assert not result.isError
    content = json.loads(result.content[0].text)
    assert len(content["results"]) == 1

@pytest.mark.asyncio
@respx.mock
async def test_call_tool_get_ficha(mock_app: Server) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Ficha/1/TEST_TOKEN"
    respx.get(mock_url).mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "CLEE": "123",
                    "Id": "1",
                    "Nombre": "OXXO",
                    "Latitud": "19.0",
                    "Clase_actividad": "Minisuper","Estrato": "0 a 5 personas","Tipo_vialidad": "Calle","Calle": "Juarez","Ubicacion": "CDMX","Tipo": "Fijo","Latitud": "19.0","Longitud": "-99.0",
                }
            ],
        )
    )

    result = await call_tool(
        "denue_get_ficha",
        {"id": "1"},
    )
    assert not result.isError
    content = json.loads(result.content[0].text)
    assert content["name"] == "OXXO"

@pytest.mark.asyncio
@respx.mock
async def test_call_tool_count_by_area_activity(mock_app: Server) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Cuantificar/09/0/0/TEST_TOKEN"
    respx.get(mock_url).mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "Actividad": "0",
                    "Area": "09",
                    "Total": "1500"
                }
            ],
        )
    )

    result = await call_tool(
        "denue_count_by_area_activity",
        {"area_code": "09"},
    )
    assert not result.isError
    content = json.loads(result.content[0].text)
    assert content["total_establishments"] == 1500

@pytest.mark.asyncio
@respx.mock
async def test_call_tool_error_handling(mock_app: Server) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Ficha/1/TEST_TOKEN"
    respx.get(mock_url).mock(return_value=httpx.Response(500))

    result = await call_tool(
        "denue_get_ficha",
        {"id": "1"},
    )
    assert result.isError
    assert "DENUE_SERVER_ERROR" in result.content[0].text

@pytest.mark.asyncio
@respx.mock
async def test_call_tool_search_by_name_radius_error(mock_app: Server) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Buscar/oxxo/19.0,-99.0/500/TEST_TOKEN"
    respx.get(mock_url).mock(return_value=httpx.Response(500))

    result = await call_tool(
        "denue_search_by_name_radius",
        {"brand_name": "oxxo", "lat": 19.0, "lon": -99.0, "radius_m": 500},
    )
    assert result.isError
    assert "DENUE_SERVER_ERROR" in result.content[0].text


@pytest.mark.asyncio
@respx.mock
async def test_call_tool_search_by_name_entity_error(mock_app: Server) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}BuscarEntidad/oxxo/09/1/100/TEST_TOKEN"
    respx.get(mock_url).mock(return_value=httpx.Response(500))

    result = await call_tool(
        "denue_search_by_name_entity",
        {"brand_name": "oxxo", "state_code": "09"},
    )
    assert result.isError
    assert "DENUE_SERVER_ERROR" in result.content[0].text

@pytest.mark.asyncio
@respx.mock
async def test_call_tool_count_by_area_activity_error(mock_app: Server) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Cuantificar/09/0/0/TEST_TOKEN"
    respx.get(mock_url).mock(return_value=httpx.Response(500))

    result = await call_tool(
        "denue_count_by_area_activity",
        {"area_code": "09"},
    )
    assert result.isError
    assert "DENUE_SERVER_ERROR" in result.content[0].text
@pytest.mark.asyncio
@respx.mock
async def test_call_tool_unexpected_error(mock_app: Server) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Buscar/oxxo/19.0,-99.0/500/TEST_TOKEN"
    respx.get(mock_url).mock(side_effect=Exception("Unexpected Exception"))

    result = await call_tool(
        "denue_search_by_name_radius",
        {"brand_name": "oxxo", "lat": 19.0, "lon": -99.0, "radius_m": 500},
    )
    assert result.isError
    assert "DENUE_SERVER_ERROR" in result.content[0].text

@pytest.mark.asyncio
@respx.mock
async def test_call_tool_search_by_name_entity_unexpected_error(mock_app: Server) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}BuscarEntidad/oxxo/09/1/100/TEST_TOKEN"
    respx.get(mock_url).mock(side_effect=Exception("Unexpected Exception"))

    result = await call_tool(
        "denue_search_by_name_entity",
        {"brand_name": "oxxo", "state_code": "09"},
    )
    assert result.isError
    assert "DENUE_SERVER_ERROR" in result.content[0].text

@pytest.mark.asyncio
@respx.mock
async def test_call_tool_get_ficha_unexpected_error(mock_app: Server) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Ficha/1/TEST_TOKEN"
    respx.get(mock_url).mock(side_effect=Exception("Unexpected Exception"))

    result = await call_tool(
        "denue_get_ficha",
        {"id": "1"},
    )
    assert result.isError
    assert "DENUE_SERVER_ERROR" in result.content[0].text

@pytest.mark.asyncio
@respx.mock
async def test_call_tool_count_by_area_activity_unexpected_error(mock_app: Server) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Cuantificar/09/0/0/TEST_TOKEN"
    respx.get(mock_url).mock(side_effect=Exception("Unexpected Exception"))

    result = await call_tool(
        "denue_count_by_area_activity",
        {"area_code": "09"},
    )
    assert result.isError
    assert "DENUE_SERVER_ERROR" in result.content[0].text
@pytest.mark.asyncio
async def test_call_tool_no_wrapper(mock_app: Server) -> None:
    # Deliberately remove the wrapper
    delattr(mock_app, "wrapper")
    result = await call_tool("denue_get_ficha", {"id": "1"})
    assert result.isError
    assert "Server not initialized correctly" in result.content[0].text
