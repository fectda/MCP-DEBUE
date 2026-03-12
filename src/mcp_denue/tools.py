from .models import EstablishmentDetail, CountResponse, SearchResponse
from .denue_client import DenueClient, DenueError
import logging

logger = logging.getLogger(__name__)


class ToolsWrapper:
    def __init__(self, client: DenueClient):
        self.client = client

    async def search_by_name_radius(
        self,
        brand_name: str,
        lat: float,
        lon: float,
        radius_m: int,
        max_results: int = 50,
    ) -> SearchResponse:
        logger.info(
            f"search_by_name_radius called: {brand_name} at {lat},{lon} in {radius_m}m"
        )
        try:
            results = await self.client.search_by_name_radius(
                brand_name, lat, lon, radius_m
            )
            truncated = len(results) > max_results
            return SearchResponse(results=results[:max_results], truncated=truncated)
        except DenueError as e:
            logger.error(f"DenueError: {e.message}")
            raise e
        except Exception as e:
            logger.exception("Unhandled error in search_by_name_radius")
            raise DenueError(str(e), "DENUE_SERVER_ERROR")

    async def search_by_name_entity(
        self,
        brand_name: str,
        state_code: str,
        municipality_code: str | None = None,
        max_results: int = 50,
    ) -> SearchResponse:
        logger.info(
            f"search_by_name_entity called: {brand_name} in {state_code}-{municipality_code}"
        )
        try:
            results = await self.client.search_by_name_entity(
                brand_name, state_code, municipality_code
            )
            truncated = len(results) > max_results
            return SearchResponse(results=results[:max_results], truncated=truncated)
        except DenueError as e:
            logger.error(f"DenueError: {e.message}")
            raise e
        except Exception as e:
            logger.exception("Unhandled error in search_by_name_entity")
            raise DenueError(str(e), "DENUE_SERVER_ERROR")

    async def get_ficha(self, id: str) -> EstablishmentDetail:
        logger.info(f"get_ficha called: {id}")
        try:
            return await self.client.get_ficha(id)
        except DenueError as e:
            logger.error(f"DenueError: {e.message}")
            raise e
        except Exception as e:
            logger.exception("Unhandled error in get_ficha")
            raise DenueError(str(e), "DENUE_SERVER_ERROR")

    async def count_by_area_activity(
        self,
        area_code: str,
        activity_id: str | None = None,
        size_class: str | None = None,
    ) -> CountResponse:
        logger.info(
            f"count_by_area_activity called: {area_code} act={activity_id} size={size_class}"
        )
        try:
            return await self.client.count_by_area_activity(
                area_code, activity_id, size_class
            )
        except DenueError as e:
            logger.error(f"DenueError: {e.message}")
            raise e
        except Exception as e:
            logger.exception("Unhandled error in count_by_area_activity")
            raise DenueError(str(e), "DENUE_SERVER_ERROR")
