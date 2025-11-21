"""Script de test pour la synchronisation des données."""
import asyncio
import sys
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Forcer le chargement du .env
from dotenv import load_dotenv
load_dotenv()

from app.tasks.sync_data import sync_all_data
from app.core.database import SessionLocal

async def main():
    """Test de synchronisation."""
    print("=" * 60)
    print("🧪 TEST DE SYNCHRONISATION DES DONNÉES")
    print("=" * 60)

    # Lancer la synchronisation
    await sync_all_data()

    # Vérifier les résultats
    print("\n" + "=" * 60)
    print("📊 VÉRIFICATION DES DONNÉES EN BASE")
    print("=" * 60)

    db = SessionLocal()
    try:
        from app.models.db import Region, Departement, Station, Line, Train, Alert

        regions_count = db.query(Region).count()
        departements_count = db.query(Departement).count()
        stations_count = db.query(Station).count()
        lines_count = db.query(Line).count()
        trains_count = db.query(Train).count()
        alerts_count = db.query(Alert).count()

        print(f"📍 Régions       : {regions_count}")
        print(f"🗺️  Départements  : {departements_count}")
        print(f"🚉 Gares         : {stations_count}")
        print(f"🚆 Lignes        : {lines_count}")
        print(f"🚄 Trains        : {trains_count}")
        print(f"⚠️  Alertes       : {alerts_count}")

        print("\n" + "=" * 60)
        if all([regions_count, departements_count, stations_count]):
            print("✅ SYNCHRONISATION RÉUSSIE !")
        else:
            print("⚠️  ATTENTION : Certaines tables sont vides")
        print("=" * 60)

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())

