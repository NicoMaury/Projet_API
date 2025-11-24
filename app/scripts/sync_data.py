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
from app.models.db import Region, Departement, Station, Line, Train
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

    def sync_stations(self, limit: int = 100, max_retries: int = 3) -> int:
        """Sync stations from SNCF Open Data API v2.1 with retry logic."""
        print("🚉 Synchronizing stations...")
        
        try:
            import requests
            import time
            
            count = 0
            offset = 0
            batch_size = 100
            seen_uic_codes = set()  # Track UIC codes to avoid duplicates
            consecutive_errors = 0
            max_consecutive_errors = 5
            
            while True:
                retry_count = 0
                success = False
                no_more_data = False
                
                while retry_count < max_retries and not success:
                    try:
                        # Use the new SNCF API v2.1
                        url = f"https://data.sncf.com/api/explore/v2.1/catalog/datasets/liste-des-gares/records"
                        params = {
                            "limit": batch_size,
                            "offset": offset
                        }
                        
                        # Augmenter le timeout à 60 secondes
                        response = requests.get(url, params=params, timeout=60)
                        response.raise_for_status()
                        data = response.json()
                        
                        results = data.get("results", [])
                        if not results:
                            print(f"   ℹ️  No more results at offset {offset}")
                            no_more_data = True
                            success = True
                            break  # No more data
                        
                        batch_added = 0
                        for item in results:
                            uic_code = item.get("code_uic")
                            if not uic_code:
                                continue
                            
                            # Skip if we've already seen this UIC code
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
                        consecutive_errors = 0  # Reset error counter on success
                        success = True
                        
                        # Check if we've reached the limit or all data
                        total_count = data.get("total_count", 0)
                        if offset >= total_count or (limit > 0 and count >= limit):
                            break
                        
                        # Petit délai pour éviter de surcharger l'API
                        time.sleep(0.1)
                    
                    except requests.exceptions.Timeout as e:
                        retry_count += 1
                        consecutive_errors += 1
                        wait_time = retry_count * 5  # Backoff exponentiel: 5s, 10s, 15s
                        
                        if retry_count < max_retries:
                            print(f"   ⚠️  Timeout at offset {offset}, retry {retry_count}/{max_retries} in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            print(f"   ❌ Max retries reached at offset {offset}, moving to next batch")
                            # Essayer de passer au batch suivant
                            offset += batch_size
                            success = True  # Continue même après erreur
                            
                    except Exception as e:
                        retry_count += 1
                        consecutive_errors += 1
                        print(f"   ❌ Error at offset {offset}: {e}")
                        
                        if retry_count < max_retries:
                            time.sleep(retry_count * 2)
                        else:
                            print(f"   ⚠️  Skipping batch at offset {offset}")
                            offset += batch_size
                            success = True
                
                # Si plus de données, on sort de la boucle principale
                if no_more_data:
                    break
                
                # Si on a trop d'erreurs consécutives, on arrête complètement
                if consecutive_errors >= max_consecutive_errors:
                    print(f"   ⚠️  Too many consecutive errors ({consecutive_errors}), stopping sync")
                    break
                
                # Si la dernière tentative a échoué et qu'on n'a pas avancé, on arrête
                if not success:
                    break

            print(f"   ✅ {count} stations synchronized (unique: {len(seen_uic_codes)})")
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

    # NOTE: Incidents/Disruptions are fetched directly from Navitia API in real-time
    # No sync needed - routes will query the API directly

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
            "lines": self.sync_lines()
        }

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 60)
        print("📊 SYNCHRONIZATION SUMMARY")
        print("=" * 60)
        for entity, count in results.items():
            print(f"   {entity.capitalize():15} : {count:5} records")
        print(f"\n   Duration: {duration:.2f} seconds")
        print(f"\n   ℹ️  Note: Incidents are fetched in real-time from Navitia API")
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
