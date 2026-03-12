import pytest
import respx
import httpx
from mcp_denue.config import Config
from mcp_denue.denue_client import DenueClient, DenueError


@pytest.fixture
def config() -> Config:
    return Config(denue_api_token="TEST_TOKEN")


@pytest.fixture
def client(config: Config) -> DenueClient:
    return DenueClient(config)


@pytest.mark.asyncio
@respx.mock
async def test_search_by_name_radius_success(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}Buscar/oxxo/19.0,-99.0/500/TEST_TOKEN"
    respx.get(mock_url).mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "CLEE": "123",
                    "Id": "1",
                    "Nombre": "OXXO",
                    "Razon_social": "Cadena Comercial OXXO",
                    "Clase_actividad": "Minisuper",
                    "Estrato": "0 a 5 personas",
                    "Tipo_vialidad": "Calle",
                    "Calle": "Juarez",
                    "Num_Exterior": "100",
                    "Num_Interior": "",
                    "Colonia": "Centro",
                    "CP": "00000",
                    "Ubicacion": "CDMX",
                    "Telefono": "",
                    "Correo_e": "",
                    "Sitio_internet": "",
                    "Tipo": "Fijo",
                    "Latitud": "19.0",
                    "Longitud": "-99.0",
                    "CentroComercial": "",
                    "TipoCentroComercial": "",
                    "NumLocal": "",
                }
            ],
        )
    )

    results = await client.search_by_name_radius("oxxo", 19.0, -99.0, 500)
    assert len(results) == 1
    assert results[0].name == "OXXO"
    assert results[0].latitude == 19.0


@pytest.mark.asyncio
@respx.mock
async def test_auth_error(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}Ficha/1/TEST_TOKEN"
    respx.get(mock_url).mock(return_value=httpx.Response(401))

    with pytest.raises(DenueError) as exc:
        await client.get_ficha("1")
    assert exc.value.type == "DENUE_AUTH_ERROR"


@pytest.mark.asyncio
@respx.mock
async def test_no_results(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}Ficha/999/TEST_TOKEN"
    respx.get(mock_url).mock(
        return_value=httpx.Response(200, json=["No se encontraron resultados"])
    )

    with pytest.raises(DenueError) as exc:
        await client.get_ficha("999")
    assert exc.value.type == "DENUE_NO_RESULTS"

@pytest.mark.asyncio
@respx.mock
async def test_search_by_name_entity_success(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}BuscarEntidad/oxxo/09/1/100/TEST_TOKEN"
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
                    "Longitud": "-99.0",
                }
            ],
        )
    )
    results = await client.search_by_name_entity("oxxo", "09")
    assert len(results) == 1
    assert results[0].name == "OXXO"

@pytest.mark.asyncio
@respx.mock
async def test_search_by_name_entity_with_municipality(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}BuscarEntidad/oxxo/09015/1/100/TEST_TOKEN"
    respx.get(mock_url).mock(return_value=httpx.Response(200, json=[]))
    results = await client.search_by_name_entity("oxxo", "09", "015")
    assert len(results) == 0

@pytest.mark.asyncio
@respx.mock
async def test_get_ficha_success(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}Ficha/1/TEST_TOKEN"
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
                    "Longitud": "-99.0",
                    "Extra_Field": "ExtraValue"
                }
            ],
        )
    )
    result = await client.get_ficha("1")
    assert result.name == "OXXO"
    assert result.extra_details["Extra_Field"] == "ExtraValue"

@pytest.mark.asyncio
@respx.mock
async def test_count_by_area_activity_success(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}Cuantificar/09/46111/0/TEST_TOKEN"
    respx.get(mock_url).mock(
        return_value=httpx.Response(200, json=[{"Actividad": "46111", "Area": "09", "Total": "1500"}])
    )
    result = await client.count_by_area_activity("09", "46111")
    assert result.total_establishments == 1500
    assert result.activity_id == "46111"

@pytest.mark.asyncio
@respx.mock
async def test_count_by_area_activity_error(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}Cuantificar/09/46111/0/TEST_TOKEN"
    respx.get(mock_url).mock(
        return_value=httpx.Response(200, json=["Error en los parametros"])
    )
    with pytest.raises(DenueError) as exc:
        await client.count_by_area_activity("09", "46111")
    assert exc.value.type == "DENUE_BAD_REQUEST"

@pytest.mark.asyncio
@respx.mock
async def test_search_by_name_entity_error(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}BuscarEntidad/oxxo/09/1/100/TEST_TOKEN"
    respx.get(mock_url).mock(
        return_value=httpx.Response(200, json=["Error de validacion"])
    )
    with pytest.raises(DenueError) as exc:
        await client.search_by_name_entity("oxxo", "09")
    assert exc.value.type == "DENUE_BAD_REQUEST"

@pytest.mark.asyncio
@respx.mock
async def test_search_by_name_radius_error(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}Buscar/oxxo/19.0,-99.0/500/TEST_TOKEN"
    respx.get(mock_url).mock(
        return_value=httpx.Response(200, json=["Error radio invalido"])
    )
    with pytest.raises(DenueError) as exc:
        await client.search_by_name_radius("oxxo", 19.0, -99.0, 500)
    assert exc.value.type == "DENUE_BAD_REQUEST"

@pytest.mark.asyncio
@respx.mock
async def test_http_rate_limit(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}Ficha/1/TEST_TOKEN"
    respx.get(mock_url).mock(return_value=httpx.Response(429))
    with pytest.raises(DenueError) as exc:
        await client.get_ficha("1")
    assert exc.value.type == "DENUE_RATE_LIMIT"

@pytest.mark.asyncio
@respx.mock
async def test_http_server_error(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}Ficha/1/TEST_TOKEN"
    respx.get(mock_url).mock(return_value=httpx.Response(500))
    with pytest.raises(DenueError) as exc:
        await client.get_ficha("1")
    assert exc.value.type == "DENUE_SERVER_ERROR"

@pytest.mark.asyncio
@respx.mock
async def test_http_bad_request(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}Ficha/1/TEST_TOKEN"
    respx.get(mock_url).mock(return_value=httpx.Response(400))
    with pytest.raises(DenueError) as exc:
        await client.get_ficha("1")
    assert exc.value.type == "DENUE_BAD_REQUEST"

@pytest.mark.asyncio
@respx.mock
async def test_http_other_error(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}Ficha/1/TEST_TOKEN"
    respx.get(mock_url).mock(return_value=httpx.Response(418)) # I'm a teapot
    with pytest.raises(DenueError) as exc:
        await client.get_ficha("1")
    assert exc.value.type == "DENUE_SERVER_ERROR"

@pytest.mark.asyncio
@respx.mock
async def test_network_error(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}Ficha/1/TEST_TOKEN"
    respx.get(mock_url).mock(side_effect=httpx.RequestError("Connection failed"))
    with pytest.raises(DenueError) as exc:
        await client.get_ficha("1")
    assert exc.value.type == "DENUE_SERVER_ERROR"

@pytest.mark.asyncio
@respx.mock
async def test_generic_exception(client: DenueClient, config: Config) -> None:
    mock_url = f"{config.denue_base_url}Ficha/1/TEST_TOKEN"
    respx.get(mock_url).mock(side_effect=Exception("Something else"))
    with pytest.raises(DenueError) as exc:
        await client.get_ficha("1")
    assert exc.value.type == "DENUE_SERVER_ERROR"
