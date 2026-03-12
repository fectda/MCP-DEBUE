import pytest
import respx
import httpx
from mcp_denue.config import Config
from mcp_denue.denue_client import DenueClient, DenueError
from mcp_denue.tools import ToolsWrapper

@pytest.fixture
def wrapper() -> ToolsWrapper:
    config = Config(denue_api_token="TEST_TOKEN")
    client = DenueClient(config)
    return ToolsWrapper(client)

@pytest.mark.asyncio
@respx.mock
async def test_search_by_name_radius_wrapper_unexpected(wrapper: ToolsWrapper) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Buscar/oxxo/19.0,-99.0/500/TEST_TOKEN"
    respx.get(mock_url).mock(side_effect=ValueError("Some unexpected internal error"))
    
    with pytest.raises(DenueError) as exc:
        await wrapper.search_by_name_radius("oxxo", 19.0, -99.0, 500)
    assert exc.value.type == "DENUE_SERVER_ERROR"

@pytest.mark.asyncio
@respx.mock
async def test_search_by_name_entity_wrapper_unexpected(wrapper: ToolsWrapper) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}BuscarEntidad/oxxo/09/1/100/TEST_TOKEN"
    respx.get(mock_url).mock(side_effect=ValueError("Some unexpected internal error"))
    
    with pytest.raises(DenueError) as exc:
        await wrapper.search_by_name_entity("oxxo", "09")
    assert exc.value.type == "DENUE_SERVER_ERROR"

@pytest.mark.asyncio
@respx.mock
async def test_get_ficha_wrapper_unexpected(wrapper: ToolsWrapper) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Ficha/1/TEST_TOKEN"
    respx.get(mock_url).mock(side_effect=ValueError("Some unexpected internal error"))
    
    with pytest.raises(DenueError) as exc:
        await wrapper.get_ficha("1")
    assert exc.value.type == "DENUE_SERVER_ERROR"

@pytest.mark.asyncio
@respx.mock
async def test_count_by_area_activity_wrapper_unexpected(wrapper: ToolsWrapper) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Cuantificar/09/0/0/TEST_TOKEN"
    respx.get(mock_url).mock(side_effect=ValueError("Some unexpected internal error"))
    
    with pytest.raises(DenueError) as exc:
        await wrapper.count_by_area_activity("09")
    assert exc.value.type == "DENUE_SERVER_ERROR"

@pytest.mark.asyncio
@respx.mock
async def test_search_by_name_radius_wrapper_denue_error(wrapper: ToolsWrapper) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Buscar/oxxo/19.0,-99.0/500/TEST_TOKEN"
    respx.get(mock_url).mock(return_value=httpx.Response(500))
    
    with pytest.raises(DenueError) as exc:
        await wrapper.search_by_name_radius("oxxo", 19.0, -99.0, 500)
    assert exc.value.type == "DENUE_SERVER_ERROR"

@pytest.mark.asyncio
@respx.mock
async def test_search_by_name_entity_wrapper_denue_error(wrapper: ToolsWrapper) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}BuscarEntidad/oxxo/09/1/100/TEST_TOKEN"
    respx.get(mock_url).mock(return_value=httpx.Response(500))
    
    with pytest.raises(DenueError) as exc:
        await wrapper.search_by_name_entity("oxxo", "09")
    assert exc.value.type == "DENUE_SERVER_ERROR"

@pytest.mark.asyncio
@respx.mock
async def test_get_ficha_wrapper_denue_error(wrapper: ToolsWrapper) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Ficha/1/TEST_TOKEN"
    respx.get(mock_url).mock(return_value=httpx.Response(500))
    
    with pytest.raises(DenueError) as exc:
        await wrapper.get_ficha("1")
    assert exc.value.type == "DENUE_SERVER_ERROR"

@pytest.mark.asyncio
@respx.mock
async def test_count_by_area_activity_wrapper_denue_error(wrapper: ToolsWrapper) -> None:
    config = Config(denue_api_token="TEST_TOKEN")
    mock_url = f"{config.denue_base_url}Cuantificar/09/0/0/TEST_TOKEN"
    respx.get(mock_url).mock(return_value=httpx.Response(500))
    
    with pytest.raises(DenueError) as exc:
        await wrapper.count_by_area_activity("09")
    assert exc.value.type == "DENUE_SERVER_ERROR"
