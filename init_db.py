"""Script d'initialisation de la base de données."""
from app.core.database import engine, Base
from app.models.db import RequestLog

def init_db():
    """Crée toutes les tables définies dans les modèles."""
    print("🔧 Initialisation de la base de données...")
    print("")

    try:
        # Créer toutes les tables
        Base.metadata.create_all(bind=engine)

        print("✅ Tables créées avec succès !")
        print("")
        print("📊 Tables disponibles :")
        print("  - request_logs : Journalisation des requêtes HTTP")
        print("")
        print("🎉 Base de données prête à l'emploi !")

    except Exception as e:
        print(f"❌ Erreur lors de la création des tables : {e}")
        return False

    return True

if __name__ == "__main__":
    success = init_db()
    exit(0 if success else 1)

