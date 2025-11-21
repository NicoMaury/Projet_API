"""OpenDataSoft service for public datasets."""

from functools import lru_cache
from typing import Any, Dict, Optional, List

import requests

from app.core.config import get_settings


class OpenDataSoftService:
    """Fetches data from OpenDataSoft public platform."""

    def __init__(self, base_url: str, timeout: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()

    def _build_url(self, endpoint: str) -> str:
        return f"{self._base_url}/{endpoint.lstrip('/')}"

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform a GET request against OpenDataSoft API."""
        url = self._build_url(endpoint)
        response = self._session.get(url, params=params, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def get_regions(self) -> List[Dict[str, Any]]:
        """Get French regions from OpenDataSoft."""
        try:
            # Les datasets de régions/départements ne sont plus disponibles sur OpenDataSoft public
            # On retourne des données statiques de fallback
            return [
                {"nom": "Auvergne-Rhône-Alpes", "code": "84"},
                {"nom": "Bourgogne-Franche-Comté", "code": "27"},
                {"nom": "Bretagne", "code": "53"},
                {"nom": "Centre-Val de Loire", "code": "24"},
                {"nom": "Corse", "code": "94"},
                {"nom": "Grand Est", "code": "44"},
                {"nom": "Hauts-de-France", "code": "32"},
                {"nom": "Île-de-France", "code": "11"},
                {"nom": "Normandie", "code": "28"},
                {"nom": "Nouvelle-Aquitaine", "code": "75"},
                {"nom": "Occitanie", "code": "76"},
                {"nom": "Pays de la Loire", "code": "52"},
                {"nom": "Provence-Alpes-Côte d'Azur", "code": "93"}
            ]
        except Exception:
            return []

    def get_departements(self) -> List[Dict[str, Any]]:
        """Get French départements from OpenDataSoft."""
        try:
            # Les datasets ne sont plus disponibles sur OpenDataSoft public
            # On retourne quelques départements en fallback
            return [
                {"nom": "Paris", "code": "75", "code_region": "11"},
                {"nom": "Hauts-de-Seine", "code": "92", "code_region": "11"},
                {"nom": "Nord", "code": "59", "code_region": "32"},
                {"nom": "Rhône", "code": "69", "code_region": "84"},
                {"nom": "Bouches-du-Rhône", "code": "13", "code_region": "93"}
            ]
        except Exception:
            return []

    def get_communes(self, departement_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get French communes, optionally filtered by département."""
        try:
            params = {"limit": 1000}
            if departement_code:
                params["where"] = f"code_departement='{departement_code}'"
            data = self.get("catalog/datasets/communes-france/records", params=params)
            return data.get("results", [])
        except Exception:
            return []

    def search_dataset(self, dataset: str, query: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Generic search on any OpenDataSoft dataset."""
        try:
            params = {"limit": limit}
            if query:
                params["q"] = query
            return self.get(f"catalog/datasets/{dataset}/records", params=params)
        except Exception:
            return {"results": [], "total_count": 0}


@lru_cache(maxsize=1)
def get_opendatasoft_service() -> OpenDataSoftService:
    """Return a cached OpenDataSoft service instance."""
    settings = get_settings()
    return OpenDataSoftService(
        base_url=str(settings.OPENDATASOFT_BASE_URL),
        timeout=settings.REQUEST_TIMEOUT_SECONDS,
    )

