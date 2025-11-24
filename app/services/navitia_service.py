"""Navitia.io API service for real-time transport data."""

from functools import lru_cache
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta

import requests

from app.core.config import get_settings


class NavitiaService:
    """Fetches real-time transport data from Navitia.io API."""

    def __init__(self, base_url: str, api_key: Optional[str], timeout: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        if api_key:
            self._session.auth = (api_key, "")

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for Navitia endpoint."""
        return f"{self._base_url}/{endpoint.lstrip('/')}"

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform a GET request against Navitia API."""
        url = self._build_url(endpoint)
        response = self._session.get(url, params=params, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def get_disruptions(self, region: str = "sncf") -> List[Dict[str, Any]]:
        """Get ALL disruptions/alerts on the network (paginated)."""
        try:
            all_disruptions = []
            start_page = 0
            count_per_page = 100  # Navitia max per page
            
            while True:
                params = {"start_page": start_page, "count": count_per_page}
                data = self.get(f"coverage/{region}/disruptions", params=params)
                disruptions = data.get("disruptions", [])
                
                if not disruptions:
                    break  # No more disruptions
                
                all_disruptions.extend(disruptions)
                
                # Check pagination info
                pagination = data.get("pagination", {})
                total_result = pagination.get("total_result", 0)
                
                if len(all_disruptions) >= total_result:
                    break  # Got all disruptions
                
                start_page += 1
            
            return all_disruptions
        except Exception:
            return []

    def get_departures(self, station_id: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get next departures from a station."""
        try:
            params = {"count": count, "data_freshness": "realtime"}
            data = self.get(f"coverage/sncf/stop_areas/{station_id}/departures", params=params)
            return data.get("departures", [])
        except Exception:
            return []

    def get_journeys(
        self,
        origin: str,
        destination: str,
        datetime_str: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get journey information between two stations."""
        try:
            params = {"from": origin, "to": destination}
            if datetime_str:
                params["datetime"] = datetime_str
            data = self.get("coverage/sncf/journeys", params=params)
            return data.get("journeys", [])
        except Exception:
            return []

    def get_lines(self, region: str = "sncf") -> List[Dict[str, Any]]:
        """Get list of ALL lines in the region (paginated)."""
        try:
            all_lines = []
            start_page = 0
            count_per_page = 100  # Navitia max per page
            
            while True:
                params = {"start_page": start_page, "count": count_per_page}
                data = self.get(f"coverage/{region}/lines", params=params)
                lines = data.get("lines", [])
                
                if not lines:
                    break  # No more lines
                
                all_lines.extend(lines)
                
                # Check pagination info
                pagination = data.get("pagination", {})
                total_result = pagination.get("total_result", 0)
                
                if len(all_lines) >= total_result:
                    break  # Got all lines
                
                start_page += 1
            
            return all_lines
        except Exception:
            return []

    def get_line_disruptions(self, line_id: str) -> List[Dict[str, Any]]:
        """Get disruptions for a specific line."""
        try:
            data = self.get(f"coverage/sncf/lines/{line_id}/disruptions")
            return data.get("disruptions", [])
        except Exception:
            return []

    def get_line_routes(self, line_id: str) -> List[Dict[str, Any]]:
        """Get routes (with stop points) for a specific line."""
        try:
            data = self.get(f"coverage/sncf/lines/{line_id}/routes")
            return data.get("routes", [])
        except Exception:
            return []


@lru_cache(maxsize=1)
def get_navitia_service() -> NavitiaService:
    """Return a cached Navitia service instance."""
    settings = get_settings()
    return NavitiaService(
        base_url=str(settings.NAVITIA_API_BASE_URL),
        api_key=settings.NAVITIA_API_KEY,
        timeout=settings.REQUEST_TIMEOUT_SECONDS,
    )

