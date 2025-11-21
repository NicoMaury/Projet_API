"""Wrapper around SNCF open data endpoints and OpenDataSoft."""

from functools import lru_cache
from typing import Any, Dict, Optional, List

import requests

from app.core.config import get_settings


class OpenDataService:
    """Fetches JSON payloads from SNCF open data endpoints."""

    def __init__(self, base_url: str, api_key: Optional[str], timeout: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        if api_key:
            self._session.headers.update({"Authorization": f"apikey {api_key}"})

    def _build_url(self, endpoint: str) -> str:
        return f"{self._base_url}/{endpoint.lstrip('/')}"

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform a GET request against the open data API."""
        url = self._build_url(endpoint)
        response = self._session.get(url, params=params, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def get_stations(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch stations from liste-des-gares dataset."""
        try:
            params = {"limit": limit, "offset": offset}
            response = self.get("catalog/datasets/liste-des-gares/records", params=params)

            # La structure réelle de l'API SNCF v2.1 retourne directement les fields
            # Normaliser la structure pour qu'elle soit compatible avec le code existant
            if "results" in response:
                normalized_results = []
                for item in response["results"]:
                    # Si les données sont directement dans item, on les encapsule
                    if "libelle" in item:  # Structure directe
                        normalized_results.append({
                            "id": item.get("code_uic", ""),
                            "record": {
                                "fields": item
                            }
                        })
                    else:  # Structure déjà encapsulée
                        normalized_results.append(item)

                return {
                    "results": normalized_results,
                    "total_count": response.get("total_count", len(normalized_results))
                }
            return response
        except Exception as e:
            print(f"Error fetching stations: {e}")
            return {"results": [], "total_count": 0}

    def search_stations(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search stations by name."""
        try:
            params = {"where": f"libelle like '{query}'", "limit": limit}
            response = self.get("catalog/datasets/liste-des-gares/records", params=params)

            # Normaliser la structure comme pour get_stations
            if "results" in response:
                normalized_results = []
                for item in response["results"]:
                    if "libelle" in item:
                        normalized_results.append({
                            "id": item.get("code_uic", ""),
                            "record": {"fields": item}
                        })
                    else:
                        normalized_results.append(item)

                return {
                    "results": normalized_results,
                    "total_count": response.get("total_count", len(normalized_results))
                }
            return response
        except Exception:
            return {"results": [], "total_count": 0}

    def get_regularite_lines(self, limit: int = 100) -> Dict[str, Any]:
        """Fetch punctuality data for lines."""
        try:
            params = {"limit": limit, "order_by": "date DESC"}
            return self.get("catalog/datasets/regularite-mensuelle-tgv-aqst/records", params=params)
        except Exception:
            return {"results": [], "total_count": 0}

    def get_delays_by_station(self, station_name: str, limit: int = 50) -> Dict[str, Any]:
        """Get delay information for a specific station."""
        try:
            params = {
                "where": f"gare like '{station_name}'",
                "limit": limit,
                "order_by": "date DESC"
            }
            return self.get("catalog/datasets/regularite-mensuelle-ter/records", params=params)
        except Exception:
            return {"results": [], "total_count": 0}

    def get_real_time_info(self, dataset: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generic method to fetch from any SNCF dataset."""
        try:
            return self.get(f"catalog/datasets/{dataset}/records", params=params)
        except Exception:
            return {"results": [], "total_count": 0}


@lru_cache(maxsize=1)
def get_opendata_service() -> OpenDataService:
    """Return a cached OpenData service instance."""
    settings = get_settings()
    return OpenDataService(
        base_url=str(settings.OPENDATA_API_BASE_URL),
        api_key=settings.OPENDATA_API_KEY,
        timeout=settings.REQUEST_TIMEOUT_SECONDS,
    )


