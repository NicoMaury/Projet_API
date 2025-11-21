"""Trains endpoints."""

from datetime import datetime, timedelta
from typing import Optional
import random

from fastapi import APIRouter, Depends, Request, HTTPException, Query

from app.core.rate_limit import limiter
from app.core.security import require_keycloak_token
from app.models.schemas import (
    TrainList, TrainDetail, Train, TrainStop, TransportMode
)
from app.services.navitia_service import get_navitia_service


router = APIRouter(
    prefix="/trains",
    tags=["Trains"],
    dependencies=[Depends(require_keycloak_token)],
)


@router.get("/", response_model=TrainList, summary="List trains")
@limiter.limit("100/minute")
async def list_trains(
    request: Request,
    limit: int = Query(50, ge=1, le=200, description="Nombre maximum de trains"),
    station_id: Optional[str] = Query(None, description="Filtrer par gare de départ"),
    status: Optional[str] = Query(None, description="Filtrer par statut")
) -> TrainList:
    """
    Récupère la liste des trains en circulation ou à venir.

    Permet de lister les trains avec filtrage optionnel par gare de départ
    et statut (scheduled, in_progress, delayed, cancelled).
    """
    try:
        navitia = get_navitia_service()

        # Simuler une liste de trains (en production: utiliser l'API temps réel SNCF)
        trains = []
        now = datetime.now()

        for i in range(min(limit, 50)):
            train_status = random.choice(["scheduled", "in_progress", "delayed", "completed"])
            if status and train_status != status:
                continue

            departure_time = now + timedelta(hours=random.randint(-2, 10))
            arrival_time = departure_time + timedelta(hours=random.randint(1, 5))

            # Modes de transport variés
            modes = [TransportMode.TGV, TransportMode.TER, TransportMode.INTERCITES, TransportMode.TRANSILIEN]
            transport_mode = random.choice(modes)

            trains.append(Train(
                id=f"TRAIN_{5000 + i}",
                number=f"{5000 + i}",
                line_id=f"LINE_{random.randint(1, 20)}",
                transport_mode=transport_mode,
                departure_station=f"STATION_{random.randint(1, 100)}",
                arrival_station=f"STATION_{random.randint(1, 100)}",
                departure_time=departure_time,
                arrival_time=arrival_time,
                status=train_status
            ))

        return TrainList(trains=trains, total=len(trains))
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch trains data: {str(e)}"
        )


@router.get("/{train_id}", response_model=TrainDetail, summary="Get train details")
@limiter.limit("100/minute")
async def get_train(train_id: str, request: Request) -> TrainDetail:
    """
    Récupère les détails complets d'un train spécifique.

    Retourne les informations détaillées du train incluant tous ses arrêts,
    les horaires prévus et réels, les retards éventuels et la composition.
    """
    try:
        navitia = get_navitia_service()

        # Extraire le numéro de train
        train_number = train_id.replace("TRAIN_", "")

        # Simuler les détails du train (en production: interroger API temps réel)
        now = datetime.now()
        departure_time = now + timedelta(hours=random.randint(0, 5))
        arrival_time = departure_time + timedelta(hours=random.randint(2, 6))

        # Générer une liste d'arrêts
        num_stops = random.randint(5, 15)
        stops = []
        current_time = departure_time

        for i in range(num_stops):
            delay_mins = random.randint(0, 15) if random.random() > 0.7 else 0

            scheduled_arr = current_time if i > 0 else None
            scheduled_dep = current_time + timedelta(minutes=2) if i < num_stops - 1 else None

            actual_arr = scheduled_arr + timedelta(minutes=delay_mins) if scheduled_arr else None
            actual_dep = scheduled_dep + timedelta(minutes=delay_mins) if scheduled_dep else None

            stops.append(TrainStop(
                station_id=f"STATION_{i+1}",
                station_name=f"Gare {i+1}",
                scheduled_arrival=scheduled_arr,
                scheduled_departure=scheduled_dep,
                actual_arrival=actual_arr,
                actual_departure=actual_dep,
                delay_minutes=delay_mins
            ))

            current_time += timedelta(minutes=random.randint(20, 45))

        current_delay = max([stop.delay_minutes for stop in stops])
        train_status = "delayed" if current_delay > 5 else "in_progress"

        # Mode de transport
        mode = TransportMode.TGV if int(train_number) >= 6000 else TransportMode.TER

        return TrainDetail(
            id=train_id,
            number=train_number,
            line_id=f"LINE_{random.randint(1, 20)}",
            transport_mode=mode,
            departure_station=stops[0].station_name if stops else None,
            arrival_station=stops[-1].station_name if stops else None,
            departure_time=departure_time,
            arrival_time=arrival_time,
            status=train_status,
            stops=stops,
            current_delay_minutes=current_delay,
            platform=f"{random.randint(1, 24)}",
            composition=f"{random.randint(6, 20)} voitures"
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch train details: {str(e)}"
        )
