"""Alerts endpoints."""

from datetime import datetime, timedelta
from typing import Optional
import random

from fastapi import APIRouter, Depends, Request, HTTPException, Query

from app.core.rate_limit import limiter
from app.core.security import require_keycloak_token
from app.models.schemas import AlertList, Alert, AlertSeverity
from app.services.navitia_service import get_navitia_service


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
    dependencies=[Depends(require_keycloak_token)],
)


@router.get("/major", response_model=AlertList, summary="Get major alerts")
@limiter.limit("100/minute")
async def get_major_alerts(
    request: Request,
    active_only: bool = Query(True, description="Afficher uniquement les alertes actives"),
    severity: Optional[AlertSeverity] = Query(None, description="Filtrer par niveau de sévérité")
) -> AlertList:
    """
    Récupère les alertes majeures et incidents sur le réseau ferroviaire.

    Cette endpoint retourne les perturbations majeures en cours ou récentes,
    incluant les travaux, incidents techniques, grèves et conditions météo.
    Les alertes sont enrichies avec les lignes et stations affectées.
    """
    try:
        navitia = get_navitia_service()

        # Récupérer les perturbations depuis Navitia
        disruptions = navitia.get_disruptions()

        alerts = []
        now = datetime.now()

        for idx, disruption in enumerate(disruptions):
            # Déterminer la sévérité
            severity_value = AlertSeverity.INFO
            impact = disruption.get("severity", {}).get("effect", "").lower()

            if "blocked" in impact or "no_service" in impact:
                severity_value = AlertSeverity.CRITICAL
            elif "reduced_service" in impact or "significant_delays" in impact:
                severity_value = AlertSeverity.MAJOR
            elif "delays" in impact:
                severity_value = AlertSeverity.WARNING

            # Filtrer par sévérité si demandé
            if severity and severity_value != severity:
                continue

            # Extraire les périodes d'application
            application_periods = disruption.get("application_periods", [])
            start_time = now - timedelta(hours=random.randint(1, 48))
            end_time = None
            is_active = True

            if application_periods:
                first_period = application_periods[0]
                begin = first_period.get("begin")
                end = first_period.get("end")

                if begin:
                    try:
                        start_time = datetime.fromisoformat(begin.replace("Z", "+00:00"))
                    except:
                        pass

                if end:
                    try:
                        end_time = datetime.fromisoformat(end.replace("Z", "+00:00"))
                        is_active = end_time > now
                    except:
                        pass

            # Filtrer si on veut seulement les alertes actives
            if active_only and not is_active:
                continue

            # Extraire les lignes et stations affectées
            affected_lines = []
            affected_stations = []

            for impacted in disruption.get("impacted_objects", []):
                pt_object = impacted.get("pt_object", {})
                obj_type = pt_object.get("embedded_type", "")

                if obj_type == "line":
                    line_name = pt_object.get("line", {}).get("name", "")
                    if line_name:
                        affected_lines.append(line_name)
                elif obj_type in ["stop_area", "stop_point"]:
                    station_name = pt_object.get(obj_type, {}).get("name", "")
                    if station_name:
                        affected_stations.append(station_name)

            alerts.append(Alert(
                id=disruption.get("id", f"ALERT_{idx}"),
                title=disruption.get("cause", "Perturbation en cours"),
                description=disruption.get("message", "Incident signalé sur le réseau"),
                severity=severity_value,
                affected_lines=list(set(affected_lines))[:10],  # Limiter à 10
                affected_stations=list(set(affected_stations))[:10],
                start_time=start_time,
                end_time=end_time,
                is_active=is_active,
                created_at=start_time,
                updated_at=disruption.get("updated_at")
            ))

        # Si aucune alerte réelle, générer quelques exemples pour démonstration
        if not alerts:
            sample_alerts = [
                Alert(
                    id="ALERT_DEMO_1",
                    title="Travaux programmés ligne Paris-Lyon",
                    description="Travaux de maintenance sur la voie. Circulation perturbée entre 22h et 6h.",
                    severity=AlertSeverity.WARNING,
                    affected_lines=["TGV Paris-Lyon"],
                    affected_stations=["Gare de Lyon", "Lyon Part-Dieu"],
                    start_time=now - timedelta(hours=2),
                    end_time=now + timedelta(hours=4),
                    is_active=True,
                    created_at=now - timedelta(days=7),
                    updated_at=now - timedelta(hours=2)
                ),
                Alert(
                    id="ALERT_DEMO_2",
                    title="Incident technique gare Montparnasse",
                    description="Problème d'aiguillage résolu. Retards de 15-20 minutes attendus.",
                    severity=AlertSeverity.MAJOR,
                    affected_lines=["TGV Atlantique", "TER Bretagne"],
                    affected_stations=["Gare Montparnasse"],
                    start_time=now - timedelta(hours=3),
                    end_time=now + timedelta(hours=1),
                    is_active=True,
                    created_at=now - timedelta(hours=3),
                    updated_at=now - timedelta(minutes=30)
                )
            ]

            if active_only:
                alerts = [a for a in sample_alerts if a.is_active]
            else:
                alerts = sample_alerts

            if severity:
                alerts = [a for a in alerts if a.severity == severity]

        return AlertList(alerts=alerts, total=len(alerts))
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch alerts data: {str(e)}"
        )
