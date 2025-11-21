"""Script to synchronize data from external APIs to PostgreSQL database."""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

from sqlalchemy.orm import Session
from sqlalchemy import select

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.database import SessionLocal, init_db
from app.models.db import Region, Departement, Station, Line, Train, Incident
from app.services.opendatasoft_service import get_opendatasoft_service
from app.services.opendata_service import get_opendata_service
from app.services.navitia_service import get_navitia_service


class DataSynchronizer:
    """Synchronize data from external APIs to PostgreSQL."""

    def __init__(self, db: Session):
        self.db = db
        self.opendata_service = get_opendata_service()
        self.navitia_service = get_navitia_service()
        self.opendatasoft_service = get_opendatasoft_service()

    def sync_regions(self) -> int:
        """Sync regions from OpenDataSoft."""
        print("🌍 Synchronizing regions...")
        
        try:
            regions_data = self.opendatasoft_service.get_regions()
            count = 0

            for item in regions_data:
                region_code = item.get("code")
                region_name = item.get("nom")

                if not region_code or not region_name:
                    continue

                # Check if region exists
                stmt = select(Region).where(Region.code == region_code)
                existing = self.db.execute(stmt).scalar_one_or_none()

                if existing:
                    existing.nom = region_name
                    existing.updated_at = datetime.now(timezone.utc)
                else:
                    region = Region(code=region_code, nom=region_name)
                    self.db.add(region)
                
                count += 1

            self.db.commit()
            print(f"   ✅ {count} regions synchronized")
            return count

        except Exception as e:
            self.db.rollback()
            print(f"   ❌ Error syncing regions: {e}")
            return 0

    def sync_departements(self) -> int:
        """Sync departments from OpenDataSoft."""
        print("🗺️  Synchronizing departments...")
        
        try:
            dept_data = self.opendatasoft_service.get_departements()
            count = 0

            for item in dept_data:
                dept_code = item.get("code")
                dept_name = item.get("nom")
                region_code = item.get("region_code")

                if not dept_code or not dept_name:
                    continue

                # Check if department exists
                stmt = select(Departement).where(Departement.code == dept_code)
                existing = self.db.execute(stmt).scalar_one_or_none()

                if existing:
                    existing.nom = dept_name
                    existing.region_code = region_code
                    existing.updated_at = datetime.now(timezone.utc)
                else:
                    dept = Departement(
                        code=dept_code,
                        nom=dept_name,
                        region_code=region_code
                    )
                    self.db.add(dept)
                
                count += 1

            self.db.commit()
            print(f"   ✅ {count} departments synchronized")
            return count

        except Exception as e:
            self.db.rollback()
            print(f"   ❌ Error syncing departments: {e}")
            return 0

    def sync_stations(self, limit: int = 100) -> int:
        """Sync stations from SNCF Open Data API v2.1."""
        print("🚉 Synchronizing stations...")
        
        try:
            import requests
            
            count = 0
            offset = 0
            batch_size = 100
            seen_uic_codes = set()  # Track UIC codes to avoid duplicates within batches
            
            while True:
                # Use the new SNCF API v2.1
                url = f"https://data.sncf.com/api/explore/v2.1/catalog/datasets/liste-des-gares/records"
                params = {
                    "limit": batch_size,
                    "offset": offset
                }
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                if not results:
                    break  # No more data
                
                batch_added = 0
                for item in results:
                    uic_code = item.get("code_uic")
                    if not uic_code:
                        continue
                    
                    # Skip if we've already seen this UIC code in this batch
                    if uic_code in seen_uic_codes:
                        continue
                    seen_uic_codes.add(uic_code)

                    name = item.get("libelle", "Unknown")
                    commune = item.get("commune")
                    dept_name = item.get("departemen")  # Note: "departemen" not "departement"

                    # Coordinates from y_wgs84 (latitude) and x_wgs84 (longitude)
                    latitude = item.get("y_wgs84")
                    longitude = item.get("x_wgs84")

                    # Check if station exists
                    stmt = select(Station).where(Station.uic_code == uic_code)
                    existing = self.db.execute(stmt).scalar_one_or_none()

                    if existing:
                        existing.name = name
                        existing.commune = commune
                        existing.departement_code = dept_name
                        existing.latitude = latitude
                        existing.longitude = longitude
                        existing.has_freight = item.get("fret", "N") == "O"
                        existing.has_passengers = item.get("voyageurs", "O") == "O"
                        existing.updated_at = datetime.now(timezone.utc)
                    else:
                        station = Station(
                            uic_code=uic_code,
                            name=name,
                            commune=commune,
                            departement_code=dept_name,
                            latitude=latitude,
                            longitude=longitude,
                            has_freight=item.get("fret", "N") == "O",
                            has_passengers=item.get("voyageurs", "O") == "O",
                            is_active=True
                        )
                        self.db.add(station)
                    
                    batch_added += 1

                # Commit every batch
                self.db.commit()
                count += batch_added
                print(f"   ⏳ {count} stations processed...")
                
                offset += batch_size
                
                # Check if we've reached the limit or all data
                total_count = data.get("total_count", 0)
                if offset >= total_count or (limit > 0 and count >= limit):
                    break

            print(f"   ✅ {count} stations synchronized")
            return count

        except Exception as e:
            self.db.rollback()
            print(f"   ❌ Error syncing stations: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def sync_lines(self) -> int:
        """Sync railway lines from Navitia."""
        print("🚆 Synchronizing lines...")
        
        try:
            lines_data = self.navitia_service.get_lines()
            count = 0
            seen_line_codes = set()  # Track line codes to avoid duplicates

            for item in lines_data:
                line_code = item.get("id")
                if not line_code:
                    continue
                
                # Skip if we've already seen this line code
                if line_code in seen_line_codes:
                    continue
                seen_line_codes.add(line_code)

                name = item.get("name", "Unknown")
                network = item.get("network", {}).get("name") if isinstance(item.get("network"), dict) else None
                color = item.get("color")
                text_color = item.get("text_color")

                # Check if line exists
                stmt = select(Line).where(Line.line_code == line_code)
                existing = self.db.execute(stmt).scalar_one_or_none()

                if existing:
                    existing.name = name
                    existing.network = network
                    existing.color = color
                    existing.text_color = text_color
                    existing.updated_at = datetime.now(timezone.utc)
                else:
                    line = Line(
                        line_code=line_code,
                        name=name,
                        network=network,
                        color=color,
                        text_color=text_color,
                        is_active=True
                    )
                    self.db.add(line)
                
                count += 1

            self.db.commit()
            print(f"   ✅ {count} lines synchronized")
            return count

        except Exception as e:
            self.db.rollback()
            print(f"   ❌ Error syncing lines: {e}")
            return 0

    def sync_incidents(self) -> int:
        """Sync incidents/disruptions from Navitia."""
        print("🚨 Synchronizing incidents...")
        
        try:
            disruptions_data = self.navitia_service.get_disruptions()
            count = 0
            seen_incident_ids = set()  # Track incident IDs to avoid duplicates

            for item in disruptions_data:
                incident_id = item.get("id")
                if not incident_id:
                    continue
                
                # Skip if we've already seen this incident ID
                if incident_id in seen_incident_ids:
                    continue
                seen_incident_ids.add(incident_id)

                # Extract line code from impacted objects
                line_code = None
                impacted = item.get("impacted_objects", [])
                if impacted and len(impacted) > 0:
                    pt_object = impacted[0].get("pt_object", {})
                    line_code = pt_object.get("id") if pt_object.get("type") == "line" else None

                title = item.get("cause", "Unknown incident")
                severity = item.get("severity", {}).get("name", "info") if isinstance(item.get("severity"), dict) else "info"
                category = item.get("category")
                status = item.get("status", "active")

                # Dates
                application_periods = item.get("application_periods", [])
                start_date = None
                end_date = None
                if application_periods and len(application_periods) > 0:
                    period = application_periods[0]
                    start_date = datetime.fromisoformat(period.get("begin").replace("Z", "+00:00")) if period.get("begin") else None
                    end_date = datetime.fromisoformat(period.get("end").replace("Z", "+00:00")) if period.get("end") else None

                # Check if incident exists
                stmt = select(Incident).where(Incident.incident_id == incident_id)
                existing = self.db.execute(stmt).scalar_one_or_none()

                if existing:
                    existing.title = title
                    existing.severity = severity
                    existing.category = category
                    existing.status = status
                    existing.start_date = start_date
                    existing.end_date = end_date
                    existing.updated_at = datetime.now(timezone.utc)
                else:
                    incident = Incident(
                        incident_id=incident_id,
                        line_code=line_code,
                        title=title,
                        description=item.get("message"),
                        severity=severity,
                        category=category,
                        status=status,
                        start_date=start_date,
                        end_date=end_date
                    )
                    self.db.add(incident)
                
                count += 1

            self.db.commit()
            print(f"   ✅ {count} incidents synchronized")
            return count

        except Exception as e:
            self.db.rollback()
            print(f"   ❌ Error syncing incidents: {e}")
            return 0

    def sync_all(self):
        """Synchronize all data sources."""
        print("=" * 60)
        print("🔄 STARTING FULL DATA SYNCHRONIZATION")
        print("=" * 60)
        
        start_time = datetime.now()

        results = {
            "regions": self.sync_regions(),
            "departements": self.sync_departements(),
            "stations": self.sync_stations(limit=0),  # 0 = no limit, get all stations
            "lines": self.sync_lines(),
            "incidents": self.sync_incidents()
        }

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 60)
        print("📊 SYNCHRONIZATION SUMMARY")
        print("=" * 60)
        for entity, count in results.items():
            print(f"   {entity.capitalize():15} : {count:5} records")
        print(f"\n   Duration: {duration:.2f} seconds")
        print("=" * 60)


def main():
    """Main function to run synchronization."""
    print("🚀 Rail Traffic Analytics - Data Synchronization")
    print()

    # Initialize database
    print("📦 Initializing database...")
    init_db()
    print("   ✅ Database initialized")
    print()

    # Create session
    db = SessionLocal()
    
    try:
        synchronizer = DataSynchronizer(db)
        synchronizer.sync_all()
    finally:
        db.close()

    print("\n✅ Synchronization completed successfully!")


if __name__ == "__main__":
    main()
