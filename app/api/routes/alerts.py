"""Alerts endpoints."""

from datetime import datetime, timedelta
from typing import Optional

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
            severity_obj = disruption.get("severity", {})
            impact = severity_obj.get("effect", "").lower() if isinstance(severity_obj, dict) else ""

            if "blocked" in impact or "no_service" in impact:
                severity_value = AlertSeverity.CRITICAL
            elif "reduced_service" in impact or "significant_delays" in impact:
                severity_value = AlertSeverity.MAJOR
            elif "delays" in impact:
                severity_value = AlertSeverity.WARNING

            # Filtrer par sévérité si demandé
            if severity and severity_value != severity:
                continue

            # Extraire le titre et la description
            # Navitia peut avoir: cause, messages, contributor
            title = ""
            description = ""
            
            # Essayer d'extraire le cause (peut être un objet avec 'label')
            cause_obj = disruption.get("cause")
            if isinstance(cause_obj, dict):
                title = cause_obj.get("label", "")
            elif isinstance(cause_obj, str):
                title = cause_obj
            
            # Essayer d'extraire les messages
            messages = disruption.get("messages", [])
            if messages and isinstance(messages, list):
                for msg in messages:
                    if isinstance(msg, dict):
                        text = msg.get("text", "")
                        if text:
                            description = text
                            break
            
            # Fallback si pas de description
            if not description:
                description = disruption.get("message", "Incident signalé sur le réseau")
            
            # Fallback si pas de titre
            if not title:
                title = severity_obj.get("name", "Perturbation en cours") if isinstance(severity_obj, dict) else "Perturbation en cours"

            # Extraire les périodes d'application
            application_periods = disruption.get("application_periods", [])
            start_time = now
            end_time = None
            is_active = True

            if application_periods:
                first_period = application_periods[0]
                begin = first_period.get("begin")
                end = first_period.get("end")

                if begin:
                    try:
                        # Format Navitia: YYYYMMDDTHHMMSS
                        start_time = datetime.strptime(begin, "%Y%m%dT%H%M%S")
                    except:
                        try:
                            start_time = datetime.fromisoformat(begin.replace("Z", "+00:00"))
                        except:
                            pass

                if end:
                    try:
                        end_time = datetime.strptime(end, "%Y%m%dT%H%M%S")
                        is_active = end_time > now
                    except:
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

            impacted_objects = disruption.get("impacted_objects", [])
            for impacted in impacted_objects:
                # L'objet impacté peut avoir plusieurs formats
                pt_object = impacted.get("pt_object", {})
                
                # Vérifier le type d'objet
                obj_id = pt_object.get("id", "")
                obj_name = pt_object.get("name", "")
                embedded_type = pt_object.get("embedded_type", "")
                
                # Extraire les lignes
                if embedded_type == "line" or "line" in obj_id.lower():
                    line_obj = pt_object.get("line", {})
                    if isinstance(line_obj, dict):
                        line_name = line_obj.get("name", obj_name)
                        if line_name:
                            affected_lines.append(line_name)
                    elif obj_name:
                        affected_lines.append(obj_name)
                
                # Extraire les stations
                elif embedded_type in ["stop_area", "stop_point"]:
                    stop_obj = pt_object.get(embedded_type, {})
                    if isinstance(stop_obj, dict):
                        station_name = stop_obj.get("name", obj_name)
                        if station_name:
                            affected_stations.append(station_name)
                    elif obj_name:
                        affected_stations.append(obj_name)

            # Parser le updated_at de Navitia (format: YYYYMMDDTHHMMSS)
            updated_at = start_time
            updated_at_str = disruption.get("updated_at")
            if updated_at_str:
                try:
                    # Format Navitia: 20251121T145715
                    updated_at = datetime.strptime(updated_at_str, "%Y%m%dT%H%M%S")
                except:
                    # Si le parsing échoue, utiliser start_time
                    updated_at = start_time

            alerts.append(Alert(
                id=disruption.get("id", f"ALERT_{idx}"),
                title=title or "Perturbation",
                description=description or "Incident signalé sur le réseau",
                severity=severity_value,
                affected_lines=list(set(affected_lines))[:10],  # Limiter à 10
                affected_stations=list(set(affected_stations))[:10],
                start_time=start_time,
                end_time=end_time,
                is_active=is_active,
                created_at=start_time,
                updated_at=updated_at
            ))

        return AlertList(alerts=alerts, total=len(alerts))
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch alerts data: {str(e)}"
        )
