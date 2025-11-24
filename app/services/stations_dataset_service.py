"""Client for the SNCF stations dataset."""

from functools import lru_cache
from typing import Any, Dict, Optional

import requests

from app.core.config import get_settings


class StationsDatasetService:
    """Fetches stations data from the SNCF open-data dataset."""

    def __init__(self, dataset_url: str, timeout: float) -> None:
        self._dataset_url = dataset_url
        self._timeout = timeout
        self._session = requests.Session()

    def fetch_records(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        where: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve station records with optional filtering parameters."""

        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if where:
            params["where"] = where
        if order_by:
            params["order_by"] = order_by

        response = self._session.get(
            self._dataset_url,
            params=params or None,
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()


@lru_cache(maxsize=1)
def get_stations_dataset_service() -> StationsDatasetService:
    """Return a cached dataset service instance."""

    settings = get_settings()
    return StationsDatasetService(
        dataset_url=str(settings.SNCF_DATASET_URL),
        timeout=settings.REQUEST_TIMEOUT_SECONDS,
    )
