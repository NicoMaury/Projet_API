"""Script de démarrage simple pour Rail Traffic Analytics."""
import uvicorn

if __name__ == "__main__":
    print("🚆 Démarrage de Rail Traffic Analytics...")
    print("📡 API disponible sur http://localhost:8000")
    print("📚 Documentation interactive sur http://localhost:8000/docs")
    print("\n⚠️  Appuyez sur CTRL+C pour arrêter\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

