"""Script d'initialisation automatique de Keycloak pour Rail Traffic Analytics."""
import requests
import time
import sys
import json
from pathlib import Path


# Configuration
KEYCLOAK_URL = "http://localhost:8080"
ADMIN_USER = "admin"
ADMIN_PASS = "admin"
REALM_NAME = "rail"
CLIENT_ID = "rail-traffic-api"
USERNAME = "testuser"
USER_PASS = "password"


def wait_for_keycloak():
    """Attendre que Keycloak soit prêt."""
    print("⏳ Attente du démarrage de Keycloak...")
    for i in range(60):
        try:
            response = requests.get(KEYCLOAK_URL, timeout=2)
            if response.status_code < 500:
                print("✅ Keycloak est prêt !")
                return True
        except:
            pass
        if i < 59:
            print(".", end="", flush=True)
        time.sleep(2)

    print("\n❌ Timeout : Keycloak n'a pas démarré")
    return False


def get_admin_token():
    """Obtenir un token admin."""
    print("🔑 Connexion admin...")
    try:
        response = requests.post(
            f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token",
            data={
                "username": ADMIN_USER,
                "password": ADMIN_PASS,
                "grant_type": "password",
                "client_id": "admin-cli"
            },
            timeout=10
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        print("✅ Token admin obtenu")
        return token
    except Exception as e:
        print(f"❌ Impossible d'obtenir le token admin: {e}")
        return None


def create_realm(token):
    """Créer le realm s'il n'existe pas."""
    print(f"\n📍 Vérification du realm '{REALM_NAME}'...")
    headers = {"Authorization": f"Bearer {token}"}

    # Vérifier si le realm existe
    try:
        response = requests.get(f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}", headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"⚠️  Le realm '{REALM_NAME}' existe déjà")
            return True
    except:
        pass

    # Créer le realm
    print(f"🔨 Création du realm '{REALM_NAME}'...")
    try:
        response = requests.post(
            f"{KEYCLOAK_URL}/admin/realms",
            headers={**headers, "Content-Type": "application/json"},
            json={
                "realm": REALM_NAME,
                "enabled": True,
                "displayName": "Rail Traffic Analytics"
            },
            timeout=10
        )
        response.raise_for_status()
        print("✅ Realm créé")
        return True
    except Exception as e:
        print(f"❌ Erreur création realm: {e}")
        return False


def get_client_uuid(token):
    """Récupérer l'UUID du client."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients",
            params={"clientId": CLIENT_ID},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        clients = response.json()
        if clients:
            return clients[0]["id"]
    except:
        pass
    return None


def create_client(token):
    """Créer le client s'il n'existe pas."""
    print(f"\n📱 Vérification du client '{CLIENT_ID}'...")
    headers = {"Authorization": f"Bearer {token}"}

    # Vérifier si le client existe
    client_uuid = get_client_uuid(token)
    if client_uuid:
        print(f"⚠️  Le client '{CLIENT_ID}' existe déjà (UUID: {client_uuid})")
        return client_uuid

    # Créer le client
    print(f"🔨 Création du client '{CLIENT_ID}'...")
    try:
        response = requests.post(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients",
            headers={**headers, "Content-Type": "application/json"},
            json={
                "clientId": CLIENT_ID,
                "enabled": True,
                "publicClient": False,
                "serviceAccountsEnabled": True,
                "directAccessGrantsEnabled": True,
                "standardFlowEnabled": True,
                "redirectUris": ["http://localhost:8000/*"],
                "webOrigins": ["*"],
                "protocol": "openid-connect"
            },
            timeout=10
        )
        response.raise_for_status()
        time.sleep(1)
        client_uuid = get_client_uuid(token)
        print(f"✅ Client créé (UUID: {client_uuid})")
        return client_uuid
    except Exception as e:
        print(f"❌ Erreur création client: {e}")
        return None


def get_client_secret(token, client_uuid):
    """Récupérer le client secret."""
    print("\n🔑 Récupération du client secret...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients/{client_uuid}/client-secret",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        secret = response.json().get("value")
        print(f"✅ Client secret : {secret}")
        return secret
    except Exception as e:
        print(f"❌ Erreur récupération secret: {e}")
        return None


def get_user_id(token, username):
    """Récupérer l'ID d'un utilisateur."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users",
            params={"username": username},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        users = response.json()
        if users:
            return users[0]["id"]
    except:
        pass
    return None


def create_user(token):
    """Créer l'utilisateur de test s'il n'existe pas."""
    print(f"\n👤 Vérification de l'utilisateur '{USERNAME}'...")
    headers = {"Authorization": f"Bearer {token}"}

    # Vérifier si l'utilisateur existe
    user_id = get_user_id(token, USERNAME)
    if user_id:
        print(f"⚠️  L'utilisateur '{USERNAME}' existe déjà")
        return True

    # Créer l'utilisateur
    print(f"🔨 Création de l'utilisateur '{USERNAME}'...")
    try:
        response = requests.post(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users",
            headers={**headers, "Content-Type": "application/json"},
            json={
                "username": USERNAME,
                "email": "test@rail.local",
                "firstName": "Test",
                "lastName": "User",
                "enabled": True,
                "emailVerified": True,
                "credentials": [{
                    "type": "password",
                    "value": USER_PASS,
                    "temporary": False
                }]
            },
            timeout=10
        )
        response.raise_for_status()
        print("✅ Utilisateur créé")
        return True
    except Exception as e:
        print(f"❌ Erreur création utilisateur: {e}")
        return False


def test_connection(client_secret):
    """Tester la connexion."""
    print("\n🧪 Test de connexion...")
    try:
        response = requests.post(
            f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": client_secret,
                "grant_type": "password",
                "username": USERNAME,
                "password": USER_PASS
            },
            timeout=10
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        if token:
            print("✅ Connexion réussie !")
            return True
    except Exception as e:
        print(f"❌ Échec du test de connexion: {e}")
    return False


def save_client_secret(client_secret):
    """Sauvegarder le client secret."""
    Path(".keycloak_secret").write_text(client_secret)
    print("\n💾 Le client secret a été sauvegardé dans : .keycloak_secret")


def print_summary(client_secret):
    """Afficher le résumé de la configuration."""
    print("\n" + "=" * 64)
    print("✅ CONFIGURATION KEYCLOAK TERMINÉE AVEC SUCCÈS !")
    print("=" * 64)
    print("\n📊 Informations de configuration :\n")
    print(f"🌐 Keycloak URL     : {KEYCLOAK_URL}")
    print(f"📍 Realm            : {REALM_NAME}")
    print(f"📱 Client ID        : {CLIENT_ID}")
    print(f"🔑 Client Secret    : {client_secret}")
    print(f"👤 Username         : {USERNAME}")
    print(f"🔒 Password         : {USER_PASS}")
    print("\n" + "=" * 64)
    print("\n🎯 Pour obtenir un token :\n")
    print(f"python get_token.py")
    print("\n" + "=" * 64)
    print("\n🚀 Vous pouvez maintenant lancer l'API avec : python start.py\n")


def main():
    """Fonction principale."""
    print("🔐 Configuration automatique de Keycloak...\n")

    # Attendre Keycloak
    if not wait_for_keycloak():
        sys.exit(1)

    # Obtenir token admin
    admin_token = get_admin_token()
    if not admin_token:
        sys.exit(1)

    # Créer realm
    if not create_realm(admin_token):
        sys.exit(1)

    # Créer client
    client_uuid = create_client(admin_token)
    if not client_uuid:
        sys.exit(1)

    # Récupérer client secret
    client_secret = get_client_secret(admin_token, client_uuid)
    if not client_secret:
        sys.exit(1)

    # Créer utilisateur
    if not create_user(admin_token):
        sys.exit(1)

    # Tester connexion
    if not test_connection(client_secret):
        sys.exit(1)

    # Sauvegarder et afficher résumé
    save_client_secret(client_secret)
    print_summary(client_secret)


if __name__ == "__main__":
    main()

