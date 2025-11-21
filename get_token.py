"""Script pour obtenir rapidement un token Keycloak."""
import requests
import sys
from pathlib import Path


def get_client_secret():
    """Récupérer le client secret depuis le fichier."""
    secret_file = Path(".keycloak_secret")
    if secret_file.exists():
        return secret_file.read_text().strip()
    return "aExfzauTdDXVBr5rVYWMy8npDSc8wfG8"  # Fallback


def get_token():
    """Obtenir un token depuis Keycloak."""
    client_secret = get_client_secret()

    try:
        response = requests.post(
            'http://localhost:8080/realms/rail/protocol/openid-connect/token',
            data={
                'client_id': 'rail-traffic-api',
                'client_secret': client_secret,
                'grant_type': 'password',
                'username': 'testuser',
                'password': 'password'
            },
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        access_token = data.get('access_token')

        if not access_token:
            print("❌ Impossible d'obtenir le token", file=sys.stderr)
            return None

        return access_token

    except requests.exceptions.ConnectionError:
        print("❌ Keycloak n'est pas accessible sur http://localhost:8080", file=sys.stderr)
        print("💡 Lancez d'abord : docker compose up -d keycloak", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la requête : {e}", file=sys.stderr)
        return None


def main():
    """Fonction principale."""
    token = get_token()

    if not token:
        sys.exit(1)

    print("✅ Token obtenu !\n")
    print(f'export TOKEN="{token}"\n')
    print("🧪 Pour tester l'API :")
    print('curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/departements')

    # Afficher aussi juste le token pour faciliter le copy-paste
    print("\n" + "=" * 60)
    print("Token (pour Swagger UI) :")
    print("=" * 60)
    print(token)


if __name__ == "__main__":
    main()

