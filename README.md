# MCP-DENUE

Un servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io) que proporciona a los agentes de IA (como Claude Desktop, Cursor, etc.) acceso a la API del DENUE de INEGI. Permite buscar y cuantificar unidades económicas (establecimientos comerciales) en México de forma estructurada.

## Requisitos
- Una llave de API de DENUE de INEGI. Puedes obtener una en el [portal oficial del INEGI](https://www.inegi.org.mx/servicios/api_denue.html).
- `uv` instalado (si usas la opción de Python) o Docker.

## Instalación y Uso (Para usuarios)

### Opción 1: Usar con `uvx` (Recomendado, no requiere clonar ni instalar dependencias)
Si tienes [uv](https://docs.astral.sh/uv/) instalado, puedes ejecutar este servidor directamente desde GitHub en cualquier cliente MCP, sin preocuparte de entornos virtuales.

Agrega esta configuración a tu cliente MCP (ej. `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mcp-denue": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/tu-usuario/mcp-denue.git",
        "mcp-denue"
      ],
      "env": {
        "DENUE_API_TOKEN": "TU_TOKEN_DEL_INEGI_AQUI"
      }
    }
  }
}
```

### Opción 2: Usar con Docker (En desarrollo)
*(Si deseas empaquetarlo como contenedor, puedes construir y ejecutar este servidor vía Docker, lo que aísla todas las dependencias).*

## Desarrollo y Pruebas (Para contribuir al repositorio)
Si quieres modificar el código de este servidor localmente:

1. Clona el repositorio.
2. Crea un entorno virtual e instala las dependencias de desarrollo:
```bash
python -m venv .venv
source .venv/bin/activate  # o .venv\Scripts\activate en Windows
pip install -e ".[dev]"
```
3. Ejecuta los tests o linters:
```bash
pytest
ruff check .
mypy src
```

## Herramientas Disponibles (Tools)
- `denue_search_by_name_radius`: Busca sucursales por nombre dentro de un radio en metros desde unas coordenadas.
- `denue_search_by_name_entity`: Busca sucursales por nombre en un estado y/o municipio de México.
- `denue_get_ficha`: Obtiene la ficha de detalle completo de un establecimiento por su ID.
- `denue_count_by_area_activity`: Cuenta el total de establecimientos en un área por giro económico.
