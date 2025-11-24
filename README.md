# Rail Traffic Analytics

Rail Traffic Analytics est une API REST développée avec FastAPI. Elle centralise les données publiques SNCF, Navitia.io et OpenDataSoft afin de fournir des informations sur les régions, départements, gares, lignes, trains en circulation, alertes et statistiques du réseau ferroviaire.

L'objectif de ce document est de permettre à une personne non technique d'installer et d'exécuter l'application du premier coup. Chaque étape est listée dans l'ordre où elle doit être réalisée.

---

## 1. Prérequis

Avant de commencer, installez les outils suivants :

- **Git** (https://git-scm.com/downloads)
- **Docker Desktop** ou Docker Engine (https://www.docker.com/get-started)
- **Python 3.12** (https://www.python.org/downloads)
- **pip** (inclus avec Python)

Assurez-vous aussi que les ports suivants sont libres :

- 8000 (API FastAPI)
- 8080 (Keycloak)
- 5432 (PostgreSQL)
- 5050 (pgAdmin, optionnel)

---

## 2. Récupération du projet

```bash
git clone https://github.com/NicoMaury/Projet_API.git
cd Projet_API
```

---

## 3. Préparation de l'environnement Python

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Configuration des variables d'environnement

1. Copier le modèle :
   ```bash
   cp .env.example .env
   ```
2. Ouvrir le fichier `.env` et vérifier les valeurs proposées. Les paramètres fournis conviennent à une installation locale. Conserver le secret Keycloak qui sera défini plus tard :
   ```env
   KEYCLOAK_CLIENT_SECRET=aExfzauTdDXVBr5rVYWMy8npDSc8wfG8
   ```

---

## 5. Démarrage des services Docker (PostgreSQL, Keycloak)

```bash
docker-compose up -d
```

- PostgreSQL : base `rail_analytics`, utilisateur `rail_user`, mot de passe `rail_password`.
- Keycloak : realm `rail` et client `rail-traffic-api` importés automatiquement (admin/admin).

Vérifier que les conteneurs sont `healthy` :
```bash
docker-compose ps
```

Si un conteneur reste en état `starting`, patienter une minute puis relancer la commande.

---

## 6. Vérification du realm `rail`

L'import automatique crée le realm et le client. Vous pouvez vérifier :

1. Ouvrir http://localhost:8080.
2. Se connecter avec `admin` / `admin`.
3. Dans le menu déroulant en haut à gauche, sélectionner `rail`.
4. Menu `Clients` → `rail-traffic-api`.
5. L’onglet `Credentials` affiche le secret déjà renseigné (`aExfzauTdDXVBr5rVYWMy8npDSc8wfG8`).

Aucune action supplémentaire n'est nécessaire tant que le fichier `keycloak-realm-import.json` n'est pas modifié.

---

## 7. Obtention d’un token d’accès (flux Client Credentials)

Aucune création d’utilisateur n’est nécessaire. L’API utilise uniquement le flux OAuth2 `client_credentials`.

Commande de test (adapter le secret si différent) :

```bash
curl -X POST http://localhost:8080/realms/rail/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=rail-traffic-api" \
  -d "client_secret=aExfzauTdDXVBr5rVYWMy8npDSc8wfG8" \
  -d "grant_type=client_credentials"
```

La réponse doit contenir un champ `access_token`. Conserver ce token pour les tests API (validité 5 minutes).

---

## 8. Lancer l’API FastAPI

```bash
python start.py
```

La console affiche l’adresse `http://localhost:8000`. La racine redirige automatiquement vers la documentation Swagger (`/docs`).

---

## 9. Tester l’API via Swagger UI

1. Aller sur http://localhost:8000/docs.
2. Cliquer sur `Authorize` (bouton en haut à droite).
3. Dans la fenêtre qui s’ouvre, renseigner uniquement le token (sans le mot `Bearer`).
4. Cliquer sur `Authorize` puis `Close`.
5. Pour chaque endpoint, cliquer sur `Try it out`, choisir les paramètres et exécuter.

Si une réponse `401 Unauthorized` apparaît, vérifier que le token n’a pas expiré.

---

## 10. Structure des principales routes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/regions` | Liste des régions françaises |
| GET | `/departements` | Liste des départements |
| GET | `/stations` | Liste paginée des gares (paramètres `limit`, `offset`, `search`) |
| GET | `/stations/{id}` | Détails d’une gare |
| GET | `/lines` | Lignes ferroviaires, filtres par région ou opérateur |
| GET | `/lines/{id}` | Détails d’une ligne |
| GET | `/trains` | Trains en circulation (agrégation Navitia) |
| GET | `/trains/{id}` | Informations détaillées d’un train |
| GET | `/stations/{id}/delays` | Statistiques de retards pour une gare |
| GET | `/lines/{id}/stats` | Performances d’une ligne |
| GET | `/stats/overview` | Vue d’ensemble du réseau |
| GET | `/alerts/major` | Alertes et incidents majeurs |

Les réponses sont sérialisées avec Pydantic et documentées automatiquement dans Swagger UI.

---

## 11. Architecture interne (résumé)

- `app/main.py` : création de l’application FastAPI, enregistrement des middlewares et redirection `/ -> /docs`.
- `app/core/security.py` : validation des tokens Keycloak (signature RS256, audience, issuer, expiration).
- `app/core/rate_limit.py` : limitation à 100 requêtes par minute et par utilisateur.
- `app/core/database.py` : configuration SQLAlchemy et journalisation des requêtes HTTP dans la table `request_logs`.
- `app/api/routes/` : toutes les routes (regions, departements, stations, lines, trains, stats, alerts).
- `app/services/` : intégrations Navitia, OpenDataSoft, SNCF Open Data.

---

## 12. Sources de données externes

| Source | Usage | Authentification |
|--------|-------|------------------|
| SNCF Open Data | Données des gares et horaires | Clé API optionnelle |
| Navitia.io | Temps réel, perturbations | Clé API obligatoire (variable `NAVITIA_API_KEY`) |
| OpenDataSoft | Régions, départements | Accès public |

Renseigner les clés correspondantes dans `.env` si nécessaire.

---

## 13. Dépannage

| Problème | Symptôme | Solution |
|----------|----------|----------|
| PostgreSQL ne démarre pas | `Exit 1` dans `docker-compose ps` | S’assurer que le port 5432 est libre. Supprimer le volume `postgres_data` si besoin (`docker volume rm projet_api_postgres_data`). |
| Keycloak ne montre pas le realm `rail` | Menu déroulant ne contient que `master` | Reprendre la section 6 pour créer manuellement le realm et le client. |
| `unauthorized_client` lors de la commande curl | Réponse JSON `error_description` | Vérifier que `Service accounts roles` est activé et que le `client_secret` est identique dans Keycloak et `.env`. |
| Réponses `401 Unauthorized` dans l’API | Swagger ou curl | Générer un nouveau token (validité 5 minutes) et vérifier l’en-tête `Authorization`. |
| Réponses `429 Too Many Requests` | Limite atteinte | Attendre 60 secondes ou réduire la fréquence des appels. |
| `ModuleNotFoundError` au lancement Python | Bibliothèques manquantes | Relancer `pip install -r requirements.txt` après activation du venv. |

---

## 14. Arrêt et nettoyage

Pour arrêter les services Docker :
```bash
docker-compose down
```

Pour supprimer toutes les données (utile pour repartir de zéro) :
```bash
docker-compose down -v
```

---

# Projet de Gaspard Pauchet, Nicolas Maury, Julian Gabry, Jean Macario et Pierre Chevalier 