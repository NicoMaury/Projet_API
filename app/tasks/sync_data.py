"""Synchronize data from external APIs to PostgreSQL database."""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
import json

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.core.database import SessionLocal
from app.models.db import Region, Departement, Station, Line, Train, Alert
from app.services.navitia_service import get_navitia_service
from app.services.opendata_service import get_opendata_service
from app.services.opendatasoft_service import get_opendatasoft_service

logger = logging.getLogger(__name__)


async def sync_all_data() -> None:
    """Synchronise toutes les données au démarrage de l'application."""
    db: Session = SessionLocal()
    try:
        logger.info("🔄 Début de la synchronisation des données...")

        # Synchronisation dans l'ordre logique
        await sync_regions(db)
        await sync_departements(db)
        await sync_stations(db)
        await sync_lines(db)
        await sync_trains(db)
        await sync_alerts(db)

        logger.info("✅ Synchronisation terminée avec succès !")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la synchronisation : {e}", exc_info=True)
    finally:
        db.close()


async def sync_regions(db: Session) -> None:
    """Synchronise les régions françaises."""
    try:
        logger.info("📍 Synchronisation des régions...")

        service = get_opendatasoft_service()
        regions_data = service.get_regions()

        count = 0
        for region_data in regions_data:
            # Utiliser insert().on_conflict_do_update() pour upsert
            stmt = insert(Region).values(
                code=region_data.get("code", ""),
                name=region_data.get("nom", ""),
                updated_at=datetime.now(timezone.utc)
            ).on_conflict_do_update(
                index_elements=['code'],
                set_=dict(
                    name=region_data.get("nom", ""),
                    updated_at=datetime.now(timezone.utc)
                )
            )
            db.execute(stmt)
            count += 1

        db.commit()
        logger.info(f"✅ {count} régions synchronisées")
    except Exception as e:
        logger.error(f"❌ Erreur régions : {e}", exc_info=True)
        db.rollback()


async def sync_departements(db: Session) -> None:
    """Synchronise les départements français."""
    try:
        logger.info("🗺️  Synchronisation des départements...")

        service = get_opendatasoft_service()
        departements_data = service.get_departements()

        count = 0
        for dept_data in departements_data:
            stmt = insert(Departement).values(
                code=dept_data.get("code", ""),
                name=dept_data.get("nom", ""),
                region_code=dept_data.get("code_region", ""),
                updated_at=datetime.now(timezone.utc)
            ).on_conflict_do_update(
                index_elements=['code'],
                set_=dict(
                    name=dept_data.get("nom", ""),
                    region_code=dept_data.get("code_region", ""),
                    updated_at=datetime.now(timezone.utc)
                )
            )
            db.execute(stmt)
            count += 1

        db.commit()
        logger.info(f"✅ {count} départements synchronisés")
    except Exception as e:
        logger.error(f"❌ Erreur départements : {e}", exc_info=True)
        db.rollback()


async def sync_stations(db: Session) -> None:
    """Synchronise les gares SNCF."""
    try:
        logger.info("🚉 Synchronisation des gares...")

        service = get_opendata_service()

        # Récupérer les stations par lots
        limit = 100
        offset = 0
        total_count = 0

        while True:
            data = service.get_stations(limit=limit, offset=offset)
            results = data.get("results", [])

            if not results:
                break

            for item in results:
                # Structure normalisée par le service
                fields = item.get("record", {}).get("fields", {})
                if not fields:
                    continue

                code_uic = fields.get("code_uic", fields.get("uic_code", ""))
                if not code_uic:
                    continue

                stmt = insert(Station).values(
                    code_uic=str(code_uic),
                    name=fields.get("libelle", fields.get("name", "Inconnu")),
                    latitude=fields.get("latitude_entreeprincipale_wgs84", fields.get("lat")),
                    longitude=fields.get("longitude_entreeprincipale_wgs84", fields.get("lon")),
                    commune=fields.get("commune", ""),
                    departement=fields.get("departement_libellemin", fields.get("departement", "")),
                    is_enabled=True,
                    updated_at=datetime.now(timezone.utc)
                ).on_conflict_do_update(
                    index_elements=['code_uic'],
                    set_=dict(
                        name=fields.get("libelle", fields.get("name", "Inconnu")),
                        latitude=fields.get("latitude_entreeprincipale_wgs84", fields.get("lat")),
                        longitude=fields.get("longitude_entreeprincipale_wgs84", fields.get("lon")),
                        commune=fields.get("commune", ""),
                        departement=fields.get("departement_libellemin", fields.get("departement", "")),
                        updated_at=datetime.now(timezone.utc)
                    )
                )
                db.execute(stmt)
                total_count += 1

            db.commit()

            # Vérifier si on a tout récupéré
            if len(results) < limit:
                break

            offset += limit

        logger.info(f"✅ {total_count} gares synchronisées")
    except Exception as e:
        logger.error(f"❌ Erreur gares : {e}", exc_info=True)
        db.rollback()


async def sync_lines(db: Session) -> None:
    """Synchronise les lignes ferroviaires."""
    try:
        logger.info("🚆 Synchronisation des lignes...")

        service = get_navitia_service()
        lines_data = service.get_lines()

        count = 0
        for line_data in lines_data:
            line_id = line_data.get("id", "")
            if not line_id:
                continue

            stmt = insert(Line).values(
                external_id=line_id,
                name=line_data.get("name", ""),
                code=line_data.get("code", ""),
                network=line_data.get("network", {}).get("name", "") if isinstance(line_data.get("network"), dict) else "",
                mode=line_data.get("physical_modes", [{}])[0].get("name", "") if line_data.get("physical_modes") else "",
                updated_at=datetime.now(timezone.utc)
            ).on_conflict_do_update(
                index_elements=['external_id'],
                set_=dict(
                    name=line_data.get("name", ""),
                    code=line_data.get("code", ""),
                    network=line_data.get("network", {}).get("name", "") if isinstance(line_data.get("network"), dict) else "",
                    mode=line_data.get("physical_modes", [{}])[0].get("name", "") if line_data.get("physical_modes") else "",
                    updated_at=datetime.now(timezone.utc)
                )
            )
            db.execute(stmt)
            count += 1

        db.commit()
        logger.info(f"✅ {count} lignes synchronisées")
    except Exception as e:
        logger.error(f"❌ Erreur lignes : {e}", exc_info=True)
        db.rollback()


async def sync_trains(db: Session) -> None:
    """Synchronise les trains en circulation (exemple avec Paris Montparnasse)."""
    try:
        logger.info("🚄 Synchronisation des trains...")

        service = get_navitia_service()

        # Exemple : récupérer les départs de Paris Montparnasse
        # Pour une vraie prod, il faudrait itérer sur plusieurs gares importantes
        station_ids = [
            "stop_area:SNCF:87391003",  # Paris Montparnasse
            "stop_area:SNCF:87686006",  # Lyon Part-Dieu
            "stop_area:SNCF:87271007",  # Marseille Saint-Charles
        ]

        count = 0
        for station_id in station_ids:
            try:
                departures = service.get_departures(station_id, count=20)

                for departure in departures:
                    display_info = departure.get("display_informations", {})
                    stop_date_time = departure.get("stop_date_time", {})

                    train_id = f"{display_info.get('network', '')}_{display_info.get('headsign', '')}_{stop_date_time.get('departure_date_time', '')}"

                    if not train_id or train_id == "__":
                        continue

                    # Calculer le retard
                    base_dt = stop_date_time.get("base_departure_date_time", "")
                    real_dt = stop_date_time.get("departure_date_time", "")
                    delay = 0
                    status = "on_time"
                    departure_time = None

                    if real_dt:
                        try:
                            departure_time = datetime.strptime(real_dt, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
                        except:
                            pass

                    if base_dt and real_dt and base_dt != real_dt:
                        try:
                            base = datetime.strptime(base_dt, "%Y%m%dT%H%M%S")
                            real = datetime.strptime(real_dt, "%Y%m%dT%H%M%S")
                            delay = int((real - base).total_seconds() / 60)
                            status = "delayed" if delay > 0 else "on_time"
                        except:
                            pass

                    stmt = insert(Train).values(
                        external_id=train_id,
                        name=display_info.get("headsign", ""),
                        line_external_id=display_info.get("network", ""),
                        direction=display_info.get("direction", ""),
                        departure_time=departure_time,
                        status=status,
                        delay_minutes=delay,
                        updated_at=datetime.now(timezone.utc)
                    ).on_conflict_do_nothing()

                    db.execute(stmt)
                    count += 1
            except Exception as e:
                logger.warning(f"⚠️  Impossible de récupérer les départs pour {station_id}: {e}")
                continue

        db.commit()
        logger.info(f"✅ {count} trains synchronisés")
    except Exception as e:
        logger.error(f"❌ Erreur trains : {e}", exc_info=True)
        db.rollback()


async def sync_alerts(db: Session) -> None:
    """Synchronise les alertes et perturbations."""
    try:
        logger.info("⚠️  Synchronisation des alertes...")

        service = get_navitia_service()
        disruptions = service.get_disruptions()

        count = 0
        for disruption in disruptions:
            disruption_id = disruption.get("id", "")
            if not disruption_id:
                continue

            # Extraire les lignes affectées
            impacted_objects = disruption.get("impacted_objects", [])
            affected_lines = []
            for obj in impacted_objects:
                pt_object = obj.get("pt_object", {})
                if pt_object.get("embedded_type") == "line":
                    affected_lines.append(pt_object.get("name", ""))

            # Déterminer la sévérité
            severity_map = {
                "information": "info",
                "warning": "warning",
                "blocking": "critical"
            }
            severity_effect = disruption.get("severity", {}).get("effect", "")
            severity = severity_map.get(severity_effect, "info")

            # Périodes d'application
            application_periods = disruption.get("application_periods", [])
            start_date = None
            end_date = None
            if application_periods:
                first_period = application_periods[0]
                begin = first_period.get("begin", "")
                end = first_period.get("end", "")
                try:
                    start_date = datetime.strptime(begin, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc) if begin else None
                    end_date = datetime.strptime(end, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc) if end else None
                except:
                    pass

            # Déterminer le statut
            status = "active"
            if end_date and end_date < datetime.now(timezone.utc):
                status = "resolved"

            stmt = insert(Alert).values(
                external_id=disruption_id,
                title=disruption.get("cause", "")[:500],
                description=json.dumps(disruption.get("messages", []), ensure_ascii=False),
                severity=severity,
                status=status,
                affected_lines=json.dumps(affected_lines, ensure_ascii=False),
                start_date=start_date,
                end_date=end_date,
                updated_at=datetime.now(timezone.utc)
            ).on_conflict_do_update(
                index_elements=['external_id'],
                set_=dict(
                    title=disruption.get("cause", "")[:500],
                    description=json.dumps(disruption.get("messages", []), ensure_ascii=False),
                    severity=severity,
                    status=status,
                    affected_lines=json.dumps(affected_lines, ensure_ascii=False),
                    start_date=start_date,
                    end_date=end_date,
                    updated_at=datetime.now(timezone.utc)
                )
            )
            db.execute(stmt)
            count += 1

        db.commit()
        logger.info(f"✅ {count} alertes synchronisées")
    except Exception as e:
        logger.error(f"❌ Erreur alertes : {e}", exc_info=True)
        db.rollback()

