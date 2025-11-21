"""Lines endpoints."""

from datetime import datetime, timedelta
from typing import Optional
import random

from fastapi import APIRouter, Depends, Request, HTTPException, Query

from app.core.rate_limit import limiter
from app.core.security import require_keycloak_token
from app.models.schemas import (
    LineList, LineDetail, Line, LineStats, TransportMode
)
from app.services.navitia_service import get_navitia_service
from app.services.opendata_service import get_opendata_service


router = APIRouter(
    prefix="/lines",
    tags=["Lines"],
    dependencies=[Depends(require_keycloak_token)],
)


@router.get("/", response_model=LineList, summary="List lines")
@limiter.limit("100/minute")
async def list_lines(
    request: Request,
    limit: int = Query(100, ge=1, le=500, description="Nombre maximum de lignes"),
    transport_mode: Optional[TransportMode] = Query(None, description="Filtrer par mode de transport")
) -> LineList:
    """
    Récupère la liste des lignes ferroviaires SNCF via Navitia.io.

    Permet de lister toutes les lignes du réseau avec filtrage optionnel
    par mode de transport (TGV, TER, Intercités, etc.).
    """
    try:
        navitia = get_navitia_service()
        raw_lines = navitia.get_lines()

        lines = []
        for item in raw_lines[:limit]:
            line_id = item.get("id", "")
            line_name = item.get("name", "Unknown")
            line_code = item.get("code", "")

            # Déterminer le mode de transport
            mode = None
            network = item.get("network", {}).get("name", "").upper()
            if "TGV" in network or "TGV" in line_name.upper():
                mode = TransportMode.TGV
            elif "TER" in network or "TER" in line_name.upper():
                mode = TransportMode.TER
            elif "INTERCITES" in network or "INTERCITÉS" in line_name.upper():
                mode = TransportMode.INTERCITES
            elif "TRANSILIEN" in network:
                mode = TransportMode.TRANSILIEN
            else:
                mode = TransportMode.TRAIN

            # Filtrer par mode si demandé
            if transport_mode and mode != transport_mode:
                continue

            lines.append(Line(
                id=line_id,
                name=line_name,
                code=line_code,
                transport_mode=mode,
                operator=item.get("network", {}).get("name", "SNCF"),
                color=item.get("color")
            ))

        return LineList(lines=lines, total=len(lines))
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch lines data: {str(e)}"
        )


@router.get("/{line_id}", response_model=LineDetail, summary="Get line details")
@limiter.limit("100/minute")
async def get_line(line_id: str, request: Request) -> LineDetail:
    """
    Récupère les détails d'une ligne ferroviaire spécifique.

    Retourne les informations complètes d'une ligne incluant ses stations,
    fréquences et horaires caractéristiques.
    """
    try:
        navitia = get_navitia_service()
        raw_lines = navitia.get_lines()

        for item in raw_lines:
            if item.get("id") == line_id:
                line_name = item.get("name", "Unknown")
                line_code = item.get("code", "")
                network = item.get("network", {}).get("name", "").upper()

                # Déterminer le mode de transport
                mode = None
                if "TGV" in network or "TGV" in line_name.upper():
                    mode = TransportMode.TGV
                elif "TER" in network or "TER" in line_name.upper():
                    mode = TransportMode.TER
                elif "INTERCITES" in network:
                    mode = TransportMode.INTERCITES
                elif "TRANSILIEN" in network:
                    mode = TransportMode.TRANSILIEN
                else:
                    mode = TransportMode.TRAIN

                # Simuler les stations de la ligne (en production: récupérer via API)
                stations = [f"Station_{i}" for i in range(random.randint(5, 20))]

                return LineDetail(
                    id=line_id,
                    name=line_name,
                    code=line_code,
                    transport_mode=mode,
                    operator=item.get("network", {}).get("name", "SNCF"),
                    color=item.get("color"),
                    stations=stations,
                    frequency="Variable selon horaires",
                    first_train="05:30",
                    last_train="23:45"
                )

        raise HTTPException(status_code=404, detail=f"Line {line_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch line details: {str(e)}"
        )


@router.get(
    "/{line_id}/stats",
    response_model=LineStats,
    summary="Get line performance statistics",
)
@limiter.limit("100/minute")
async def get_line_stats(
    line_id: str,
    request: Request,
    days: int = Query(30, ge=1, le=90, description="Nombre de jours d'historique")
) -> LineStats:
    """
    Analyse les performances d'une ligne ferroviaire sur une période donnée.

    Retourne des statistiques détaillées incluant le taux de ponctualité,
    les retards moyens, les suppressions et les incidents recensés.
    """
    try:
        navitia = get_navitia_service()
        opendata = get_opendata_service()

        # Récupérer le nom de la ligne
        line_name = "Unknown"
        raw_lines = navitia.get_lines()
        for item in raw_lines:
            if item.get("id") == line_id:
                line_name = item.get("name", "Unknown")
                break

        # Récupérer les disruptions
        disruptions = navitia.get_line_disruptions(line_id)
        incidents_count = len(disruptions)

        # Simuler des statistiques (en production: interroger bases de données historiques)
        period_end = datetime.now()
        period_start = period_end - timedelta(days=days)

        total_trains = random.randint(500, 2000)
        on_time_trains = random.randint(int(total_trains * 0.7), int(total_trains * 0.9))
        delayed_trains = random.randint(10, total_trains - on_time_trains)
        cancelled_trains = total_trains - on_time_trains - delayed_trains

        punctuality_rate = round(on_time_trains / total_trains * 100, 2)
        avg_delay = random.uniform(8.0, 20.0)

        return LineStats(
            line_id=line_id,
            line_name=line_name,
            period_start=period_start,
            period_end=period_end,
            total_trains=total_trains,
            on_time_trains=on_time_trains,
            delayed_trains=delayed_trains,
            cancelled_trains=cancelled_trains,
            punctuality_rate=punctuality_rate,
            average_delay_minutes=round(avg_delay, 2),
            incidents_count=incidents_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch line statistics: {str(e)}"
        )
