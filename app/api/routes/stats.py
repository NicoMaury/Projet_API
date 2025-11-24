"""System-wide statistics endpoints."""

from datetime import datetime
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel

from app.core.rate_limit import limiter
from app.core.security import require_keycloak_token
from app.core.database import get_db
from app.models.db import Station, Line, Train
from app.services.navitia_service import get_navitia_service


class NetworkOverview(BaseModel):
    """Overview statistics for the entire rail network."""
    total_stations: int
    total_lines: int
    active_trains: int
    active_alerts: int
    global_punctuality_rate: float
    average_delay_minutes: float
    updated_at: datetime


router = APIRouter(
    prefix="/stats",
    tags=["Statistics"],
    dependencies=[Depends(require_keycloak_token)],
)


@router.get("/overview", response_model=NetworkOverview, summary="Get global statistics overview")
@limiter.limit("100/minute")
async def get_stats_overview(request: Request, db: Session = Depends(get_db)) -> NetworkOverview:
    """
    Récupère une vue d'ensemble des statistiques du réseau ferroviaire SNCF.

    Cette endpoint agrège les données de toutes les sources pour fournir
    une vision globale de l'état du réseau : nombre de gares, lignes, trains
    en circulation, alertes actives, et indicateurs de performance globaux.
    """
    try:
        navitia = get_navitia_service()

        # Récupérer les données depuis la base de données
        total_stations = db.query(Station).filter(Station.is_active == True).count()
        total_lines = db.query(Line).filter(Line.is_active == True).count()
        
        # Récupérer les trains actifs depuis la DB
        active_trains = db.query(Train).filter(Train.is_active == True).count()

        # Récupérer les alertes actives depuis Navitia (live)
        disruptions = navitia.get_disruptions()
        active_alerts = len(disruptions)

        # Calculer la ponctualité moyenne depuis les trains en DB
        delayed_trains = db.query(Train).filter(
            Train.is_active == True,
            Train.delay_minutes > 0
        ).count()
        
        if active_trains > 0:
            on_time_trains = active_trains - delayed_trains
            global_punctuality = round((on_time_trains / active_trains) * 100, 2)
        else:
            global_punctuality = 100.0
        
        # Calculer le retard moyen
        trains_with_delays = db.query(Train).filter(
            Train.is_active == True,
            Train.delay_minutes > 0
        ).all()
        
        if trains_with_delays:
            avg_delay = sum(t.delay_minutes for t in trains_with_delays) / len(trains_with_delays)
        else:
            avg_delay = 0.0

        return NetworkOverview(
            total_stations=total_stations,
            total_lines=total_lines,
            active_trains=active_trains if active_trains > 0 else 0,
            active_alerts=active_alerts,
            global_punctuality_rate=global_punctuality,
            average_delay_minutes=round(avg_delay, 2),
            updated_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch statistics overview: {str(e)}"
        )
