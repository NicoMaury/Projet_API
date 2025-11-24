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
        """Get ALL French départements (101 total including DOM-TOM)."""
        try:
            # Liste complète des départements français (métropole + DOM-TOM)
            departements = [
                # Île-de-France
                {"nom": "Paris", "code": "75", "region_code": "11"},
                {"nom": "Seine-et-Marne", "code": "77", "region_code": "11"},
                {"nom": "Yvelines", "code": "78", "region_code": "11"},
                {"nom": "Essonne", "code": "91", "region_code": "11"},
                {"nom": "Hauts-de-Seine", "code": "92", "region_code": "11"},
                {"nom": "Seine-Saint-Denis", "code": "93", "region_code": "11"},
                {"nom": "Val-de-Marne", "code": "94", "region_code": "11"},
                {"nom": "Val-d'Oise", "code": "95", "region_code": "11"},
                # Auvergne-Rhône-Alpes
                {"nom": "Ain", "code": "01", "region_code": "84"},
                {"nom": "Allier", "code": "03", "region_code": "84"},
                {"nom": "Ardèche", "code": "07", "region_code": "84"},
                {"nom": "Cantal", "code": "15", "region_code": "84"},
                {"nom": "Drôme", "code": "26", "region_code": "84"},
                {"nom": "Isère", "code": "38", "region_code": "84"},
                {"nom": "Loire", "code": "42", "region_code": "84"},
                {"nom": "Haute-Loire", "code": "43", "region_code": "84"},
                {"nom": "Puy-de-Dôme", "code": "63", "region_code": "84"},
                {"nom": "Rhône", "code": "69", "region_code": "84"},
                {"nom": "Savoie", "code": "73", "region_code": "84"},
                {"nom": "Haute-Savoie", "code": "74", "region_code": "84"},
                # Bourgogne-Franche-Comté
                {"nom": "Côte-d'Or", "code": "21", "region_code": "27"},
                {"nom": "Doubs", "code": "25", "region_code": "27"},
                {"nom": "Jura", "code": "39", "region_code": "27"},
                {"nom": "Nièvre", "code": "58", "region_code": "27"},
                {"nom": "Haute-Saône", "code": "70", "region_code": "27"},
                {"nom": "Saône-et-Loire", "code": "71", "region_code": "27"},
                {"nom": "Yonne", "code": "89", "region_code": "27"},
                {"nom": "Territoire de Belfort", "code": "90", "region_code": "27"},
                # Bretagne
                {"nom": "Côtes-d'Armor", "code": "22", "region_code": "53"},
                {"nom": "Finistère", "code": "29", "region_code": "53"},
                {"nom": "Ille-et-Vilaine", "code": "35", "region_code": "53"},
                {"nom": "Morbihan", "code": "56", "region_code": "53"},
                # Centre-Val de Loire
                {"nom": "Cher", "code": "18", "region_code": "24"},
                {"nom": "Eure-et-Loir", "code": "28", "region_code": "24"},
                {"nom": "Indre", "code": "36", "region_code": "24"},
                {"nom": "Indre-et-Loire", "code": "37", "region_code": "24"},
                {"nom": "Loir-et-Cher", "code": "41", "region_code": "24"},
                {"nom": "Loiret", "code": "45", "region_code": "24"},
                # Corse
                {"nom": "Corse-du-Sud", "code": "2A", "region_code": "94"},
                {"nom": "Haute-Corse", "code": "2B", "region_code": "94"},
                # Grand Est
                {"nom": "Ardennes", "code": "08", "region_code": "44"},
                {"nom": "Aube", "code": "10", "region_code": "44"},
                {"nom": "Marne", "code": "51", "region_code": "44"},
                {"nom": "Haute-Marne", "code": "52", "region_code": "44"},
                {"nom": "Meurthe-et-Moselle", "code": "54", "region_code": "44"},
                {"nom": "Meuse", "code": "55", "region_code": "44"},
                {"nom": "Moselle", "code": "57", "region_code": "44"},
                {"nom": "Bas-Rhin", "code": "67", "region_code": "44"},
                {"nom": "Haut-Rhin", "code": "68", "region_code": "44"},
                {"nom": "Vosges", "code": "88", "region_code": "44"},
                # Hauts-de-France
                {"nom": "Aisne", "code": "02", "region_code": "32"},
                {"nom": "Nord", "code": "59", "region_code": "32"},
                {"nom": "Oise", "code": "60", "region_code": "32"},
                {"nom": "Pas-de-Calais", "code": "62", "region_code": "32"},
                {"nom": "Somme", "code": "80", "region_code": "32"},
                # Normandie
                {"nom": "Calvados", "code": "14", "region_code": "28"},
                {"nom": "Eure", "code": "27", "region_code": "28"},
                {"nom": "Manche", "code": "50", "region_code": "28"},
                {"nom": "Orne", "code": "61", "region_code": "28"},
                {"nom": "Seine-Maritime", "code": "76", "region_code": "28"},
                # Nouvelle-Aquitaine
                {"nom": "Charente", "code": "16", "region_code": "75"},
                {"nom": "Charente-Maritime", "code": "17", "region_code": "75"},
                {"nom": "Corrèze", "code": "19", "region_code": "75"},
                {"nom": "Creuse", "code": "23", "region_code": "75"},
                {"nom": "Dordogne", "code": "24", "region_code": "75"},
                {"nom": "Gironde", "code": "33", "region_code": "75"},
                {"nom": "Landes", "code": "40", "region_code": "75"},
                {"nom": "Lot-et-Garonne", "code": "47", "region_code": "75"},
                {"nom": "Pyrénées-Atlantiques", "code": "64", "region_code": "75"},
                {"nom": "Deux-Sèvres", "code": "79", "region_code": "75"},
                {"nom": "Vienne", "code": "86", "region_code": "75"},
                {"nom": "Haute-Vienne", "code": "87", "region_code": "75"},
                # Occitanie
                {"nom": "Ariège", "code": "09", "region_code": "76"},
                {"nom": "Aude", "code": "11", "region_code": "76"},
                {"nom": "Aveyron", "code": "12", "region_code": "76"},
                {"nom": "Gard", "code": "30", "region_code": "76"},
                {"nom": "Haute-Garonne", "code": "31", "region_code": "76"},
                {"nom": "Gers", "code": "32", "region_code": "76"},
                {"nom": "Hérault", "code": "34", "region_code": "76"},
                {"nom": "Lot", "code": "46", "region_code": "76"},
                {"nom": "Lozère", "code": "48", "region_code": "76"},
                {"nom": "Hautes-Pyrénées", "code": "65", "region_code": "76"},
                {"nom": "Pyrénées-Orientales", "code": "66", "region_code": "76"},
                {"nom": "Tarn", "code": "81", "region_code": "76"},
                {"nom": "Tarn-et-Garonne", "code": "82", "region_code": "76"},
                # Pays de la Loire
                {"nom": "Loire-Atlantique", "code": "44", "region_code": "52"},
                {"nom": "Maine-et-Loire", "code": "49", "region_code": "52"},
                {"nom": "Mayenne", "code": "53", "region_code": "52"},
                {"nom": "Sarthe", "code": "72", "region_code": "52"},
                {"nom": "Vendée", "code": "85", "region_code": "52"},
                # Provence-Alpes-Côte d'Azur
                {"nom": "Alpes-de-Haute-Provence", "code": "04", "region_code": "93"},
                {"nom": "Hautes-Alpes", "code": "05", "region_code": "93"},
                {"nom": "Alpes-Maritimes", "code": "06", "region_code": "93"},
                {"nom": "Bouches-du-Rhône", "code": "13", "region_code": "93"},
                {"nom": "Var", "code": "83", "region_code": "93"},
                {"nom": "Vaucluse", "code": "84", "region_code": "93"},
            ]
            return departements
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

