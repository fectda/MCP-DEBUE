import httpx
from typing import List, Optional, Any
from .config import Config
from .models import (
    DenueEstablishmentRaw,
    Establishment,
    EstablishmentDetail,
    CountResponse,
)


class DenueError(Exception):
    def __init__(self, message: str, type: str):
        super().__init__(message)
        self.message = message
        self.type = type


class DenueClient:
    def __init__(self, config: Config):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.denue_base_url, timeout=config.request_timeout
        )

    def _handle_error(self, e: Exception, url: str) -> None:
        if isinstance(e, httpx.HTTPStatusError):
            if e.response.status_code == 401 or e.response.status_code == 403:
                raise DenueError("Missing or invalid token.", "DENUE_AUTH_ERROR")
            elif e.response.status_code == 429:
                raise DenueError("Rate limit exceeded.", "DENUE_RATE_LIMIT")
            elif e.response.status_code >= 500:
                raise DenueError("Upstream service failure.", "DENUE_SERVER_ERROR")
            elif e.response.status_code == 400:
                raise DenueError("Invalid parameters.", "DENUE_BAD_REQUEST")
            else:
                raise DenueError(
                    f"HTTP Error: {e.response.status_code}", "DENUE_SERVER_ERROR"
                )
        elif isinstance(e, httpx.RequestError):
            raise DenueError(
                f"Network error while connecting to DENUE: {str(e)}",
                "DENUE_SERVER_ERROR",
            )
        else:
            raise DenueError(f"Unexpected error: {str(e)}", "DENUE_SERVER_ERROR")

    async def _get(self, endpoint: str) -> Any:
        # Strip token from logging
        safe_endpoint = endpoint.replace(self.config.denue_api_token, "***")
        # Ensure we don't have multiple slashes
        endpoint = endpoint.lstrip("/")

        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._handle_error(e, safe_endpoint)

    async def search_by_name_radius(
        self, brand_name: str, lat: float, lon: float, radius: int
    ) -> List[Establishment]:
        """Buscar/{condicion}/{latitud},{longitud}/{metros}/{token}"""
        token = self.config.denue_api_token
        condicion = brand_name if brand_name else "todos"
        endpoint = f"Buscar/{condicion}/{lat},{lon}/{radius}/{token}"

        data = await self._get(endpoint)

        if not data:
            return []

        if (
            isinstance(data, list)
            and len(data) == 1
            and isinstance(data[0], str)
            and "Error" in data[0]
        ):
            # Usually INEGI returns an array with an error string if not found or bad params
            raise DenueError(f"DENUE returned error: {data[0]}", "DENUE_BAD_REQUEST")

        # Often DENUE returns a simple string "No se encontraron resultados" or similar in a 1-element list
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
            return []

        results = []
        for item in data:
            try:
                raw = DenueEstablishmentRaw(**item)
                results.append(Establishment.from_raw(raw))
            except Exception:
                continue

        return results

    async def search_by_name_entity(
        self, brand_name: str, state_code: str, municipality_code: Optional[str] = None
    ) -> List[Establishment]:
        """BuscarEntidad/{condicion}/{entidad}/{registro_inicial}/{registro_final}/{token}"""
        # Usually entity search just takes condition, entity
        # The pagination parameters: 1 to max_results. We'll fetch up to max_results_default + something, but the PRD says simple pagination or truncation.
        token = self.config.denue_api_token
        condicion = brand_name if brand_name else "todos"

        # If municipality is not provided, use entity code. The INEGI API expects 'entidad' code.
        # It's not standard BuscarEntidad has municipality unless it's a 5-digit code.
        entidad = state_code
        if municipality_code:
            entidad = f"{state_code}{municipality_code}"

        # We will request 1 to 500 records max per PRD recommendation
        start = 1
        end = self.config.max_results_default * 2  # fetch some margin

        endpoint = f"BuscarEntidad/{condicion}/{entidad}/{start}/{end}/{token}"
        data = await self._get(endpoint)

        if not data:
            return []

        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
            if "Error" in data[0]:
                raise DenueError(
                    f"DENUE returned error: {data[0]}", "DENUE_BAD_REQUEST"
                )
            return []

        results = []
        for item in data:
            try:
                raw = DenueEstablishmentRaw(**item)
                results.append(Establishment.from_raw(raw))
            except Exception:
                continue
        return results

    async def get_ficha(self, id: str) -> EstablishmentDetail:
        """Ficha/{id}/{token}"""
        token = self.config.denue_api_token
        endpoint = f"Ficha/{id}/{token}"

        data = await self._get(endpoint)
        if not data or (
            isinstance(data, list) and len(data) > 0 and isinstance(data[0], str)
        ):
            raise DenueError(f"Establishment {id} not found.", "DENUE_NO_RESULTS")

        item = data[0] if isinstance(data, list) else data
        raw = DenueEstablishmentRaw(**item)
        base = Establishment.from_raw(raw)

        # Any fields not in base go to extra_details
        extra_details = {
            k: v for k, v in item.items() if k not in DenueEstablishmentRaw.model_fields
        }
        return EstablishmentDetail(**base.model_dump(), extra_details=extra_details)

    async def count_by_area_activity(
        self,
        area_code: str,
        activity_id: Optional[str] = None,
        size_class: Optional[str] = None,
    ) -> CountResponse:
        """Cuantificar/{area}/{actividad}/{estrato}/{token}"""
        token = self.config.denue_api_token
        area = area_code if area_code else "00"
        actividad = activity_id if activity_id else "0"
        estrato = size_class if size_class else "0"

        endpoint = f"Cuantificar/{area}/{actividad}/{estrato}/{token}"

        data = await self._get(endpoint)

        if not data or (
            isinstance(data, list) and len(data) > 0 and isinstance(data[0], str)
        ):
            # "Error" or "0"
            if isinstance(data, list) and "Error" in str(data[0]):
                raise DenueError(
                    f"DENUE returned error: {data[0]}", "DENUE_BAD_REQUEST"
                )
            return CountResponse(
                activity_id=actividad, area_code=area, total_establishments=0
            )

        # The Count response from INEGI API usually looks like:
        # Field 1: Id de la actividad económica
        # Field 2: Clave del área geográfica
        # Field 3: Total de establecimientos
        # e.g. [{"Actividad": "0", "Area": "00", "Total": "110685"}] or similar fields
        item = data[0] if isinstance(data, list) else data

        # Extract the fields based on what they might be called, or fallback
        total = 0
        for k, v in item.items():
            if str(k).lower() in ["total", "cantidad", "count"]:
                total = int(v)
            # if no named key, take the last key or the one with number
            if isinstance(v, (int, str)) and str(v).isdigit() and int(v) > total:
                # heuristic
                total = int(v)

        return CountResponse(
            activity_id=actividad, area_code=area, total_establishments=total
        )
