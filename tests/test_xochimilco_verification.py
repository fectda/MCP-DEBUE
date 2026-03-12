import pytest
import respx
import json
import httpx
from mcp_denue.server import app, call_tool
from mcp_denue.config import Config
from mcp_denue.denue_client import DenueClient
from mcp_denue.tools import ToolsWrapper

@pytest.fixture
def mock_app():
    config = Config(denue_api_token="VALID_TOKEN")
    client = DenueClient(config)
    # Ensure ToolsWrapper is registered
    setattr(app, "wrapper", ToolsWrapper(client))
    return app

@pytest.mark.asyncio
@respx.mock
async def test_xochimilco_oxxo_search(mock_app):
    """
    Specific verification for:
    - brand_name: oxxo
    - state_code: 09 (CDMX)
    - municipality_code: 013 (Xochimilco)
    """
    config = Config(denue_api_token="VALID_TOKEN")
    # The API should be called with state 09
    mock_url = f"{config.denue_base_url}BuscarEntidad/oxxo/09/1/100/VALID_TOKEN"
    
    respx.get(mock_url).mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "CLEE": "090131234567", # Xochi
                    "Id": "101",
                    "Nombre": "OXXO XOCHIMILCO CENTRO",
                    "Clase_actividad": "Minisuper",
                    "Estrato": "11 a 30 personas",
                    "Tipo_vialidad": "CALLE",
                    "Calle": "MORELOS",
                    "Ubicacion": "XOCHIMILCO, CIUDAD DE MÉXICO",
                    "Tipo": "FIJO",
                    "Latitud": "19.25",
                    "Longitud": "-99.10",
                },
                {
                    "CLEE": "090159876543", # NOT Xochi (Cuauhtémoc 015)
                    "Id": "102",
                    "Nombre": "OXXO REFORMA",
                    "Clase_actividad": "Minisuper",
                    "Estrato": "11 a 30 personas",
                    "Tipo_vialidad": "AVENIDA",
                    "Calle": "REFORMA",
                    "Ubicacion": "CUAUHTÉMOC, CIUDAD DE MÉXICO",
                    "Tipo": "FIJO",
                    "Latitud": "19.43",
                    "Longitud": "-99.14",
                }
            ],
        )
    )

    result = await call_tool(
        "denue_search_by_name_entity",
        {
            "brand_name": "oxxo",
            "state_code": "09",
            "municipality_code": "013"
        },
    )

    assert not result.isError
    data = json.loads(result.content[0].text)
    
    # Should only return the Xochimilco one (CLEE starting with 09013)
    results = data["results"]
    assert len(results) == 1
    assert results[0]["name"] == "OXXO XOCHIMILCO CENTRO"
    assert results[0]["clee"].startswith("09013")
    print(f"\nVerification Success: Found {len(results)} Oxxos in Xochimilco (013)")
