"""Trains endpoints."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.rate_limit import limiter
from app.core.security import require_keycloak_token
from app.core.database import get_db
from app.models.db import Train as DBTrain, Station as DBStation
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
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200, description="Nombre maximum de trains"),
    station_id: Optional[str] = Query(None, description="Filtrer par gare de départ"),
    status: Optional[str] = Query(None, description="Filtrer par statut")
) -> TrainList:
    """
    Récupère la liste des trains en circulation ou à venir depuis la base de données.

    Permet de lister les trains avec filtrage optionnel par gare de départ
    et statut (scheduled, in_progress, delayed, cancelled).
    """
    try:
        # Si une gare est spécifiée, récupérer les départs en temps réel via Navitia
        if station_id:
            navitia = get_navitia_service()
            departures = navitia.get_departures(station_id, count=limit)
            
            trains = []
            for dep in departures:
                stop_point = dep.get("stop_point", {})
                route = dep.get("route", {})
                line = route.get("line", {})
                
                # Déterminer le statut
                stop_date_time = dep.get("stop_date_time", {})
                departure_time_str = stop_date_time.get("departure_date_time")
                base_departure_str = stop_date_time.get("base_departure_date_time")
                
                train_status = "scheduled"
                if departure_time_str and base_departure_str:
                    try:
                        actual = datetime.strptime(departure_time_str, "%Y%m%dT%H%M%S")
                        scheduled = datetime.strptime(base_departure_str, "%Y%m%dT%H%M%S")
                        if actual > scheduled:
                            train_status = "delayed"
                    except:
                        pass
                
                trains.append(Train(
                    id=route.get("id", ""),
                    number=route.get("name", ""),
                    line_id=line.get("id", ""),
                    transport_mode=TransportMode.TRAIN,
                    departure_station=stop_point.get("name", station_id),
                    arrival_station=route.get("direction", {}).get("name", ""),
                    departure_time=datetime.strptime(departure_time_str, "%Y%m%dT%H%M%S") if departure_time_str else datetime.now(),
                    arrival_time=None,
                    status=train_status
                ))
            
            return TrainList(trains=trains, total=len(trains))
        
        # Sinon, récupérer depuis la DB
        query = db.query(DBTrain).filter(DBTrain.is_active == True)
        
        if status:
            query = query.filter(DBTrain.status == status)
        
        total = query.count()
        db_trains = query.order_by(DBTrain.departure_time.desc()).limit(limit).all()
        
        trains = []
        for db_train in db_trains:
            # Déterminer le mode de transport (simplification)
            mode = TransportMode.TRAIN
            if db_train.train_number and db_train.train_number.startswith("TGV"):
                mode = TransportMode.TGV
            elif db_train.train_number and db_train.train_number.startswith("TER"):
                mode = TransportMode.TER
            
            trains.append(Train(
                id=str(db_train.id),
                number=db_train.train_number,
                line_id=db_train.line_code or "",
                transport_mode=mode,
                departure_station=db_train.origin or "",
                arrival_station=db_train.destination or "",
                departure_time=db_train.departure_time,
                arrival_time=db_train.arrival_time,
                status=db_train.status or "scheduled"
            ))

        return TrainList(trains=trains, total=total)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch trains data: {str(e)}"
        )


@router.get("/{train_id}", response_model=TrainDetail, summary="Get train details")
@limiter.limit("100/minute")
async def get_train(train_id: str, request: Request, db: Session = Depends(get_db)) -> TrainDetail:
    """
    Récupère les détails complets d'un train spécifique.

    Retourne les informations détaillées du train incluant tous ses arrêts,
    les horaires prévus et réels, les retards éventuels et la composition.
    """
    try:
        # Essayer de récupérer depuis la DB
        db_train = None
        try:
            train_id_int = int(train_id)
            db_train = db.query(DBTrain).filter(DBTrain.id == train_id_int).first()
        except ValueError:
            # L'ID n'est pas un nombre, chercher par numéro de train
            db_train = db.query(DBTrain).filter(DBTrain.train_number == train_id).first()
        
        if db_train:
            # Déterminer le mode de transport
            mode = TransportMode.TRAIN
            if db_train.train_number and db_train.train_number.startswith("TGV"):
                mode = TransportMode.TGV
            elif db_train.train_number and db_train.train_number.startswith("TER"):
                mode = TransportMode.TER
            
            # Note: Les arrêts détaillés ne sont pas stockés en DB, 
            # ils devraient être récupérés via Navitia en temps réel
            stops = []
            
            return TrainDetail(
                id=str(db_train.id),
                number=db_train.train_number,
                line_id=db_train.line_code or "",
                transport_mode=mode,
                departure_station=db_train.origin or "",
                arrival_station=db_train.destination or "",
                departure_time=db_train.departure_time,
                arrival_time=db_train.arrival_time,
                status=db_train.status or "scheduled",
                stops=stops,
                current_delay_minutes=db_train.delay_minutes,
                platform="N/A",  # Info non disponible en DB
                composition="N/A"  # Info non disponible en DB
            )
        
        # Si pas trouvé en DB, retourner une erreur
        raise HTTPException(
            status_code=404, 
            detail=f"Train {train_id} not found. Note: Real-time train tracking requires integration with SNCF real-time APIs."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch train details: {str(e)}"
        )
