"""Script de test pour vérifier que toutes les APIs sont accessibles."""

import sys
from app.services.opendata_service import get_opendata_service
from app.services.navitia_service import get_navitia_service
from app.services.opendatasoft_service import get_opendatasoft_service

def test_sncf_opendata():
    """Test SNCF Open Data API."""
    print("\n🧪 Test SNCF Open Data (data.sncf.com)...")
    try:
        service = get_opendata_service()
        result = service.get_stations(limit=5)

        if result.get("results"):
            total = result.get("total_count", 0)
            print(f"   ✅ SNCF Open Data OK - {total} gares disponibles")

            # Essayer d'afficher un exemple
            first_result = result['results'][0]
            station_name = "N/A"

            # Structure peut varier selon l'API
            if 'record' in first_result:
                station_name = first_result['record'].get('fields', {}).get('libelle', 'N/A')
            elif 'fields' in first_result:
                station_name = first_result['fields'].get('libelle', 'N/A')
            elif 'libelle' in first_result:
                station_name = first_result['libelle']

            print(f"   📊 Exemple: {station_name}")
            print(f"   📦 Structure: {list(first_result.keys())}")
            return True
        else:
            print("   ⚠️  SNCF Open Data - Aucune donnée retournée")
            return False
    except Exception as e:
        print(f"   ❌ SNCF Open Data ERREUR: {e}")
        import traceback
        print(f"   🐛 Détails: {traceback.format_exc()[:200]}")
        return False

def test_navitia():
    """Test Navitia.io API."""
    print("\n🧪 Test Navitia.io (api.navitia.io)...")
    try:
        service = get_navitia_service()

        # Test des lignes
        lines = service.get_lines()
        if lines:
            print(f"   ✅ Navitia.io OK - {len(lines)} lignes récupérées")
            print(f"   📊 Exemple: {lines[0].get('name', 'N/A')}")
        else:
            print("   ⚠️  Navitia.io - Aucune ligne retournée (clé API manquante ?)")

        # Test des perturbations
        disruptions = service.get_disruptions()
        print(f"   📡 Perturbations actives: {len(disruptions)}")

        return len(lines) > 0
    except Exception as e:
        print(f"   ❌ Navitia.io ERREUR: {e}")
        print("   💡 Vérifiez votre NAVITIA_API_KEY dans .env")
        return False

def test_opendatasoft():
    """Test OpenDataSoft API."""
    print("\n🧪 Test OpenDataSoft (public.opendatasoft.com)...")
    try:
        service = get_opendatasoft_service()

        # Test régions
        regions = service.get_regions()
        if regions:
            print(f"   ✅ OpenDataSoft OK - {len(regions)} régions récupérées")

            # Afficher la structure
            first_region = regions[0]
            region_name = "N/A"

            if 'record' in first_region:
                region_name = first_region['record'].get('fields', {}).get('nom', 'N/A')
            elif 'fields' in first_region:
                region_name = first_region['fields'].get('nom', 'N/A')
            elif 'nom' in first_region:
                region_name = first_region['nom']

            print(f"   📊 Exemple: {region_name}")
            print(f"   📦 Structure: {list(first_region.keys())}")
        else:
            print("   ⚠️  OpenDataSoft - Aucune région retournée")

        # Test départements
        departements = service.get_departements()
        print(f"   📡 Départements disponibles: {len(departements)}")

        return len(regions) > 0
    except Exception as e:
        print(f"   ❌ OpenDataSoft ERREUR: {e}")
        import traceback
        print(f"   🐛 Détails: {traceback.format_exc()[:200]}")
        return False

def main():
    """Execute tous les tests."""
    print("=" * 60)
    print("🔍 TEST DE CONNEXION AUX APIs")
    print("=" * 60)

    results = {
        "SNCF Open Data": test_sncf_opendata(),
        "Navitia.io": test_navitia(),
        "OpenDataSoft": test_opendatasoft()
    }

    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)

    for api, success in results.items():
        status = "✅ OK" if success else "❌ ERREUR"
        print(f"   {api:20} : {status}")

    all_ok = all(results.values())

    print("\n" + "=" * 60)
    if all_ok:
        print("🎉 TOUTES LES APIs FONCTIONNENT CORRECTEMENT!")
        print("=" * 60)
        return 0
    else:
        print("⚠️  CERTAINES APIs NE SONT PAS ACCESSIBLES")
        print("=" * 60)
        print("\n💡 Actions recommandées:")
        if not results["SNCF Open Data"]:
            print("   - Vérifier la connexion internet")
            print("   - Vérifier OPENDATA_API_BASE_URL dans .env")
        if not results["Navitia.io"]:
            print("   - Obtenir une clé API sur https://www.navitia.io/")
            print("   - Ajouter NAVITIA_API_KEY dans .env")
        if not results["OpenDataSoft"]:
            print("   - Vérifier OPENDATASOFT_BASE_URL dans .env")
        return 1

if __name__ == "__main__":
    sys.exit(main())
