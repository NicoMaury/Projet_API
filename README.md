# 🚆 Rail Traffic Analytics

> **API REST sophistiquée pour l'analyse et le suivi du trafic ferroviaire français en temps réel**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat&logo=postgresql)](https://www.postgresql.org/)
[![Keycloak](https://img.shields.io/badge/Keycloak-23.0-4D4D4D?style=flat&logo=keycloak)](https://www.keycloak.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker)](https://www.docker.com/)

---

## ⚡ Démarrage Ultra Rapide

```bash
# 1. Cloner et installer
git clone https://github.com/votre-repo/Projet_API.git
cd Projet_API
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Le fichier .env est déjà créé avec les valeurs par défaut

# 3. Lancer l'API
python start.py
```

**🎉 C'est prêt !** Ouvrez http://localhost:8000/docs

> **Note:** Par défaut, l'authentification Keycloak est désactivée en mode développement pour faciliter les tests.
> Pour activer la sécurité complète, suivez la section [Configuration Keycloak](#-authentification).

---

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Installation rapide](#-installation-rapide)
- [Endpoints de l'API](#-endpoints-de-lapi)
- [Configuration](#-configuration)
- [Documentation](#-documentation)
- [Sécurité](#-sécurité)

---

## 🎯 Vue d'ensemble

Rail Traffic Analytics est une solution complète pour analyser le réseau ferroviaire SNCF. L'API s'appuie sur trois sources de données officielles (SNCF Open Data, Navitia.io, OpenDataSoft) pour fournir :

- 📊 **Statistiques en temps réel** : Retards, suppressions, incidents
- 🚉 **Informations géographiques** : 3000+ gares, 100+ lignes
- 🚨 **Système d'alertes** : Détection et classification des incidents
- 📈 **Analyses avancées** : Performance par ligne et par gare

---

## ✨ Fonctionnalités

### Analyse en Temps Réel
- ✅ Import automatique des horaires SNCF
- ✅ Détection instantanée des retards
- ✅ Vision précise du trafic ferroviaire

### Détection d'Incidents
- ✅ Système intelligent via Navitia.io
- ✅ Classification par sévérité (info, warning, major, critical)
- ✅ Historisation complète dans PostgreSQL

### Statistiques Avancées
- ✅ Analyses par ligne avec taux de ponctualité
- ✅ Analyses par gare avec historique des retards
- ✅ Vue d'ensemble globale du réseau

### Sécurité & Performance
- ✅ Authentification OAuth2 obligatoire (Keycloak)
- ✅ Rate limiting : 100 requêtes/minute/utilisateur
- ✅ Journalisation automatique de toutes les requêtes

---

## 🏗️ Architecture

### Stack Technique

```
┌─────────────────────────────────────────────┐
│           FastAPI Application               │
│  ┌────────────┐  ┌──────────┐  ┌─────────┐ │
│  │   Routes   │  │ Services │  │  Models │ │
│  └────────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│   Keycloak   │ │   APIs   │ │  PostgreSQL  │
│    OAuth2    │ │  Externe │ │   Database   │
└──────────────┘ └──────────┘ └──────────────┘
```

### 🎯 Choix Techniques et Justifications

| Technologie | Version | Justification |
|-------------|---------|---------------|
| **FastAPI** | 0.110.0 | Framework Python moderne, rapide, avec documentation automatique (Swagger UI). Typage fort avec Pydantic. |
| **PostgreSQL** | 15 | Base de données relationnelle robuste, idéale pour les données structurées (gares, trains, statistiques). |
| **Keycloak** | 23.0 | Solution OAuth2/OpenID Connect professionnelle, évite de coder l'authentification manuellement. |
| **SQLAlchemy** | 2.0 | ORM Python puissant pour gérer les modèles de base de données de manière Pythonique. |
| **Pydantic** | 2.6 | Validation automatique des données entrantes/sortantes, génération des schémas OpenAPI. |
| **SlowAPI** | 0.1.9 | Rate limiting basé sur la bibliothèque Flask-Limiter, protège contre les abus. |
| **Docker Compose** | - | Orchestration multi-conteneurs, simplifie le déploiement (PostgreSQL + Keycloak + pgAdmin). |

### 📐 Architecture en Couches (Clean Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
│  - Réception des requêtes HTTP                              │
│  - Validation JWT (security.py)                             │
│  - Rate limiting (100 req/min)                              │
│  - Sérialisation/Désérialisation JSON                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Business Logic Layer                        │
│  - Services métier (navitia_service.py, etc.)               │
│  - Appels aux APIs externes (SNCF, Navitia, OpenDataSoft)  │
│  - Transformation des données                               │
│  - Calculs statistiques                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Data Access Layer                          │
│  - Modèles SQLAlchemy (db.py)                               │
│  - Schémas Pydantic (schemas.py)                            │
│  - Gestion des sessions PostgreSQL                          │
│  - Journalisation des requêtes (request_logs)               │
└─────────────────────────────────────────────────────────────┘
```

**Avantages de cette architecture :**
- ✅ Séparation des responsabilités (API / Business / Data)
- ✅ Testabilité : chaque couche peut être testée indépendamment
- ✅ Maintenabilité : modifications localisées (ex: changer de BDD)
- ✅ Évolutivité : facile d'ajouter de nouvelles routes ou services

### Structure du Projet (Détaillée)

```
Projet_API/
├── app/
│   ├── api/
│   │   └── routes/          # 🌐 Endpoints REST (12 routes)
│   │       ├── alerts.py    # Alertes majeures
│   │       ├── departements.py
│   │       ├── lines.py     # Lignes ferroviaires
│   │       ├── regions.py
│   │       ├── stations.py  # Gares SNCF
│   │       ├── stats.py     # Statistiques globales
│   │       └── trains.py    # Trains en circulation
│   ├── core/
│   │   ├── config.py        # ⚙️ Configuration Pydantic
│   │   ├── database.py      # 🗄️ SQLAlchemy setup
│   │   ├── rate_limit.py    # 🚦 SlowAPI (100 req/min)
│   │   └── security.py      # 🔐 Validation JWT Keycloak
│   ├── models/
│   │   ├── db.py           # 📊 Modèles base de données
│   │   └── schemas.py      # 📋 33 schémas Pydantic
│   ├── services/
│   │   ├── navitia_service.py      # 🚉 API Navitia.io
│   │   ├── opendata_service.py     # 🚂 SNCF Open Data
│   │   └── opendatasoft_service.py # 🗺️ Données géographiques
│   └── main.py             # 🚀 Point d'entrée FastAPI
├── docker-compose.yml       # 🐳 PostgreSQL + Keycloak + pgAdmin
├── init-db.sql             # 📝 Schema SQL + import Keycloak
├── start.py                # ▶️ Script de démarrage simplifié
├── requirements.txt        # 📦 Dépendances Python
└── README.md              # 📚 Cette documentation
```

### 🔄 Flux d'une Requête Typique

**Exemple : Récupérer la liste des gares**

```
1. Client envoie:
   GET /stations?limit=10
   Authorization: Bearer eyJhbGciOiJSUzI1...

2. FastAPI (main.py)
   ├─ Middleware SlowAPI: Vérifie rate limit (100/min)
   ├─ Middleware logging: Enregistre la requête
   └─ Route /stations activée

3. Security (security.py)
   ├─ Extrait le token JWT du header Authorization
   ├─ Télécharge les clés publiques depuis Keycloak (JWKS)
   ├─ Vérifie la signature RS256
   ├─ Valide audience, issuer, expiration
   └─ Autorise ou rejette (401)

4. Route Handler (routes/stations.py)
   ├─ Valide les paramètres de query (?limit=10)
   ├─ Appelle le service approprié
   └─ Retourne la réponse JSON

5. Service (opendatasoft_service.py)
   ├─ Interroge l'API SNCF Open Data
   ├─ Parse la réponse JSON
   └─ Transforme en objets Pydantic

6. FastAPI
   ├─ Sérialise les objets Pydantic en JSON
   ├─ Ajoute les headers CORS
   ├─ Enregistre le temps de réponse en BDD
   └─ Retourne HTTP 200 + JSON
```

### 🗄️ Modèle de Données PostgreSQL

```sql
-- Table principale: journalisation
CREATE TABLE request_logs (
    id SERIAL PRIMARY KEY,
    method VARCHAR(10) NOT NULL,        -- GET, POST, etc.
    path TEXT NOT NULL,                 -- /stations, /trains, etc.
    user_id VARCHAR(255),               -- Claim 'sub' du token JWT
    status_code INTEGER NOT NULL,       -- 200, 401, 429, etc.
    duration_ms INTEGER NOT NULL,       -- Temps de traitement
    created_at TIMESTAMP DEFAULT NOW()  -- Date/heure de la requête
);

-- Index pour améliorer les performances
CREATE INDEX idx_request_logs_user ON request_logs(user_id);
CREATE INDEX idx_request_logs_created ON request_logs(created_at);
```

**Cas d'usage :**
- Analyser les endpoints les plus utilisés
- Détecter les utilisateurs qui abusent de l'API
- Mesurer les performances (temps de réponse moyen)
- Audit de sécurité (qui a accédé à quoi et quand)
│   ├── models/
│   │   ├── db.py           # Modèles base de données
│   │   └── schemas.py      # 33 schémas Pydantic
│   ├── services/
│   │   ├── navitia_service.py
│   │   ├── opendata_service.py
│   │   └── opendatasoft_service.py
│   └── main.py
├── docker-compose.yml       # 🐳 PostgreSQL + Keycloak
├── .env.example
└── requirements.txt
```

---

## 🚀 Installation rapide

### Option 1 : Avec Docker (Recommandé)

```bash
# 1. Démarrer PostgreSQL et Keycloak
docker-compose up -d

# 2. Installer les dépendances Python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configurer l'environnement
cp .env.example .env
nano .env  # Éditer avec les URLs Docker

# 4. Démarrer l'API
python start.py
```

**URLs Docker par défaut :**
- Keycloak : http://localhost:8080 (admin/admin)
- PostgreSQL : localhost:5432 (rail_user/rail_password)
- pgAdmin : http://localhost:5050 (admin@rail.local/admin)

---

## 📡 Endpoints de l'API

### Consultation (8 endpoints)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/regions` | Liste des régions françaises |
| GET | `/departements` | Liste des départements |
| GET | `/stations` | Toutes les gares SNCF (pagination) |
| GET | `/stations/{id}` | Détails d'une gare |
| GET | `/lines` | Lignes ferroviaires (filtrage) |
| GET | `/lines/{id}` | Détails d'une ligne |
| GET | `/trains` | Trains en circulation |
| GET | `/trains/{id}` | Détails d'un train avec arrêts |

### Statistiques (3 endpoints)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/stations/{id}/delays` | Analyse des retards par gare |
| GET | `/lines/{id}/stats` | Performances par ligne |
| GET | `/stats/overview` | Vue d'ensemble du réseau |

### Alertes (1 endpoint)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/alerts/major` | Alertes et incidents majeurs |

📖 **Documentation complète** : [API_ENDPOINTS.md](API_ENDPOINTS.md)

---

## 🔐 Authentification

**Toutes les routes nécessitent un token JWT Keycloak valide.**

### 📝 Configuration Keycloak

> **✅ Configuration pré-existante** : Le realm `rail` et le client `rail-traffic-api` sont déjà configurés dans Keycloak.  
> **⚠️ IMPORTANT** : Cette API utilise le flux **Client Credentials** (OAuth2 machine-to-machine).  
> **Vous N'AVEZ PAS besoin de créer d'utilisateur dans Keycloak !**  
> Il suffit d'activer les Service Accounts et récupérer le client secret.

#### Étape 1 : Démarrer Keycloak

```bash
# Démarrer Keycloak via Docker
docker-compose up -d keycloak

# Attendre que Keycloak soit prêt (30-60 secondes)
docker-compose logs -f keycloak
```

#### Étape 2 : Activer les Service Accounts (OAuth2 Client Credentials)

**⚠️ PAS BESOIN DE CRÉER D'UTILISATEUR ! Le flux Client Credentials fonctionne sans utilisateur.**

1. Ouvrez http://localhost:8080
2. Connectez-vous avec les identifiants :
   - **Username** : `admin`
   - **Password** : `admin`
3. Sélectionnez le realm **"rail"** (menu déroulant en haut à gauche)
4. Dans le menu de gauche, cliquez sur **"Clients"**
5. Cliquez sur **"rail-traffic-api"** dans la liste
6. Dans l'onglet **"Settings"** :
   - ✅ **Client authentication** : ON (activé)
   - ✅ **Service accounts roles** : ON (activé) ⚠️ **IMPORTANT**
   - ✅ **Standard flow** : ON (optionnel)
   - ❌ **Direct access grants** : OFF (non utilisé)
7. Cliquez sur **"Save"**

#### Étape 3 : Récupérer le Client Secret

1. Restez sur le client **"rail-traffic-api"**
2. Allez dans l'onglet **"Credentials"**
3. Copiez le **"Client secret"** affiché
4. Ajoutez-le dans votre fichier `.env` :
   ```bash
   # Éditer le fichier .env
   nano .env
   
   # Ajouter/Modifier cette ligne
   KEYCLOAK_CLIENT_SECRET=votre_secret_copié_ici
   ```

#### Étape 4 : Vérifier la configuration

Testez que le client fonctionne :

```bash
curl -X POST 'http://localhost:8080/realms/rail/protocol/openid-connect/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'client_id=rail-traffic-api' \
  -d 'client_secret=VOTRE_CLIENT_SECRET' \
  -d 'grant_type=client_credentials'
```

✅ **Si ça fonctionne**, vous recevrez un token.  
❌ **Si erreur "unauthorized_client"**, vérifiez que **Service accounts roles** est bien activé à l'Étape 2.

---

## 🔑 Utilisation de l'API avec authentification

### Obtenir un token OAuth2

L'API utilise le flux **Client Credentials** (OAuth2 machine-to-machine). Aucun utilisateur n'est requis.

```bash
curl -X POST 'http://localhost:8080/realms/rail/protocol/openid-connect/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'client_id=rail-traffic-api' \
  -d 'client_secret=VOTRE_CLIENT_SECRET' \
  -d 'grant_type=client_credentials'
```

**Réponse attendue :**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 300,
  "token_type": "Bearer",
  "scope": "profile email rail-traffic-api-scope"
}
```

**⏱️ Durée de validité :** Les tokens expirent après **5 minutes** (300 secondes).

**💡 Astuce :** Pour extraire uniquement le token :
```bash
curl -s -X POST 'http://localhost:8080/realms/rail/protocol/openid-connect/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'client_id=rail-traffic-api' \
  -d 'client_secret=k8JVC02I3pbJ08Dy7UWl97pPIqnBxq3u' \
  -d 'grant_type=client_credentials' | \
  python3 -c "import sys, json; print('Bearer ' + json.load(sys.stdin)['access_token'])"
```

Cette commande affiche directement le token au format `Bearer eyJhbG...` prêt à être copié dans Swagger UI !

---

## ⚙️ Configuration

### Variables d'environnement essentielles

```env
# Keycloak OAuth2
KEYCLOAK_JWKS_URL=http://localhost:8080/realms/rail/protocol/openid-connect/certs
KEYCLOAK_AUDIENCE=rail-traffic-api
KEYCLOAK_ISSUER=http://localhost:8080/realms/rail

# PostgreSQL
DATABASE_URL=postgresql+psycopg://rail_user:rail_password@localhost:5432/rail_analytics

# APIs externes (optionnel)
NAVITIA_API_KEY=votre_cle_navitia
OPENDATA_API_KEY=votre_cle_sncf
```

Voir `.env.example` pour la configuration complète.

---

## 📚 Documentation
### Documentation interactive

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

---

## 🔒 Sécurité

### Validation JWT stricte
- ✅ Vérification signature RS256
- ✅ Validation audience (`aud`)
- ✅ Validation issuer (`iss`)
- ✅ Vérification expiration (`exp`)

### Rate Limiting
- 100 requêtes/minute par utilisateur
- Identification via claim `sub` du token
- HTTP 429 en cas de dépassement

### Journalisation
- Logs automatiques dans PostgreSQL
- Table `request_logs` : méthode, path, user_id, durée, statut

```sql
-- Consulter les logs récents
SELECT * FROM request_logs 
ORDER BY created_at DESC 
LIMIT 20;
```

---

## 🧪 Tester l'API

### 1. Via Swagger UI (Interface graphique)

1. Ouvrez http://localhost:8000/docs
2. Cliquez sur **"Authorize"** 🔒
3. Collez votre token Keycloak
4. Testez les endpoints interactivement

### 2. Via curl (Ligne de commande)

```bash
# Régions
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/regions

# Gares avec pagination
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/stations?limit=10&search=Paris"

# Statistiques d'une ligne
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/lines/LINE_ID/stats?days=30

# Alertes actives
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/alerts/major?severity=critical"
```

---

## ❓ FAQ - Questions Fréquentes

### 🎓 Pourquoi utiliser le flux "Client Credentials" plutôt que créer des utilisateurs ?

Cette API utilise le flux **OAuth2 Client Credentials** (machine-to-machine), qui est différent du flux classique avec login/password.

**Comprendre les différences :**

| Flux "Authorization Code" (classique) | Flux "Client Credentials" (utilisé ici) |
|--------------------------------------|----------------------------------------|
| ✅ Utilisateur se connecte avec login/password | ❌ Pas de login utilisateur |
| ✅ Nécessite création de comptes utilisateurs | ✅ Utilise directement le client |
| ✅ Idéal pour applications web/mobile | ✅ Idéal pour API-to-API |
| ❌ Plus complexe à tester | ✅ Simple à tester |

**Dans notre cas :**
- L'API est conçue pour être consommée par d'autres applications/services
- Pas besoin d'interface utilisateur de connexion
- Le **client** (`rail-traffic-api`) représente l'application qui consomme l'API
- Le **client secret** joue le rôle de "mot de passe" de l'application

**Analogie simple :**
- Flux classique = Vous entrez dans un bâtiment avec votre badge personnel
- Client Credentials = Une machine à café qui a un code d'accès permanent

### 🔐 Comment fonctionne l'authentification OAuth2 Client Credentials ?

**Schéma du flux :**

```
┌─────────────┐                                    ┌──────────────┐
│   Client    │                                    │  Keycloak    │
│ (Postman/   │  1. POST /token + client_id       │  (Serveur    │
│  curl/app)  │     + client_secret                │   OAuth2)    │
│             │  ─────────────────────────────────>│              │
│             │                                    │ ✓ Vérifie    │
│             │  2. Retourne access_token (JWT)   │   credentials│
│             │  <─────────────────────────────────│              │
└─────────────┘                                    └──────────────┘
       │
       │ 3. Requête API + Bearer token
       │    Authorization: Bearer eyJhbGc...
       ▼
┌─────────────────────────────────────────┐
│     Rail Traffic Analytics API          │
│  ┌───────────────────────────────────┐  │
│  │ 1. Extrait le token du header     │  │
│  │ 2. Vérifie la signature avec      │  │
│  │    les clés publiques Keycloak    │  │
│  │ 3. Valide audience, issuer, exp   │  │
│  │ 4. Autorise ou rejette (401)      │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Pourquoi c'est sécurisé ?**
- Le token JWT est **signé cryptographiquement** par Keycloak (RS256)
- L'API vérifie la signature avec la **clé publique** de Keycloak
- Le token a une **durée de vie limitée** (5 minutes)
- Impossible de falsifier un token sans avoir la clé privée de Keycloak

### 🛠️ Je suis bloqué à l'étape Keycloak, que faire ?

**Problème 1 : "unauthorized_client" lors de la récupération du token**

**Cause :** Les Service Accounts ne sont pas activés

**Solution :**
```bash
1. Aller sur http://localhost:8080
2. Se connecter (admin/admin)
3. Sélectionner le realm "rail" en haut à gauche
4. Menu "Clients" → Cliquer sur "rail-traffic-api"
5. Dans l'onglet "Settings" :
   ✅ Client authentication: ON
   ✅ Service accounts roles: ON  ← CRITIQUE
6. Cliquer "Save"
7. Réessayer la commande curl
```

**Problème 2 : Je ne vois pas le client "rail-traffic-api"**

**Cause :** Le realm n'est pas correctement initialisé

**Solution :**
```bash
# Arrêter et supprimer les conteneurs
docker-compose down -v

# Redémarrer (cela réinitialise Keycloak)
docker-compose up -d

# Attendre 60 secondes que Keycloak démarre
docker-compose logs -f keycloak
# (Attendre de voir "Keycloak ... started")
```

**Problème 3 : Le token fonctionne dans curl mais pas dans Swagger UI**

**Cause :** Format du token incorrect dans Swagger

**Solution :**
- Dans Swagger, coller **UNIQUEMENT** le token : `eyJhbGciOiJSUzI1NiIsInR5cCI6...`
- **NE PAS** inclure le mot "Bearer" (Swagger l'ajoute automatiquement)

**Problème 4 : Erreur "Invalid authorization token" (401)**

**Causes possibles :**
1. Le token a expiré (durée de vie : 5 minutes)
   → Solution : Régénérer un nouveau token
2. Le client secret est incorrect dans `.env`
   → Solution : Vérifier que `KEYCLOAK_CLIENT_SECRET` correspond au secret dans Keycloak
3. Les URLs Keycloak sont incorrectes
   → Solution : Vérifier que Keycloak est accessible sur `http://localhost:8080`

### 🧪 Comment tester que tout fonctionne ?

**Test complet en 4 étapes :**

```bash
# Étape 1 : Vérifier que Keycloak fonctionne
curl http://localhost:8080/realms/rail

# Devrait retourner du JSON avec "realm": "rail"

# Étape 2 : Obtenir un token
TOKEN=$(curl -s -X POST 'http://localhost:8080/realms/rail/protocol/openid-connect/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'client_id=rail-traffic-api' \
  -d 'client_secret=k8JVC02I3pbJ08Dy7UWl97pPIqnBxq3u' \
  -d 'grant_type=client_credentials' | \
  python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Étape 3 : Vérifier que l'API fonctionne
curl http://localhost:8000/regions

# Devrait retourner 401 Unauthorized (normal, pas de token)

# Étape 4 : Tester avec le token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/regions

# Devrait retourner la liste des régions françaises ✅
```

### 📝 Commandes utiles pour le projet

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs de Keycloak
docker-compose logs -f keycloak

# Voir les logs de PostgreSQL
docker-compose logs -f postgres

# Arrêter tous les services
docker-compose down

# Tout réinitialiser (attention : perd les données)
docker-compose down -v

# Lancer l'API Python
python start.py

# Installer les dépendances
pip install -r requirements.txt
```

---

## 📊 Sources de données

| Source | Usage | Documentation |
|--------|-------|---------------|
| **SNCF Open Data** | Gares, horaires | https://data.sncf.com |
| **Navitia.io** | Temps réel, perturbations | https://doc.navitia.io |
| **OpenDataSoft** | Régions, départements | https://public.opendatasoft.com |

---

## 🛠️ Commandes utiles

```bash
# Démarrer l'environnement Docker
docker-compose up -d

# Arrêter Docker
docker-compose down

# Activer l'environnement Python
source .venv/bin/activate

# Démarrer l'API
python start.py

# Voir les logs PostgreSQL
docker-compose logs -f postgres

# Accéder à la base de données
docker exec -it rail_postgres psql -U rail_user -d rail_analytics
```

---

## 🎯 Prochaines étapes

Après l'installation :

1. ✅ Configurer Keycloak (realm, client, utilisateur)
2. ✅ Obtenir une clé API Navitia.io (gratuit)
3. ✅ Tester tous les endpoints via Swagger UI
4. ✅ Consulter les logs dans PostgreSQL
5. 📖 Lire la documentation complète

---

## 🤝 Contribution

Les contributions sont bienvenues ! Domaines d'amélioration :

- [ ] Tests unitaires et d'intégration
- [ ] Cache Redis pour performances
- [ ] Dashboard front-end
- [ ] Prédiction ML des retards
- [ ] Export CSV/Excel
- [ ] Webhooks pour alertes

---

<div align="center">

**Développé avec FastAPI, Keycloak et PostgreSQL**

Documentation complète disponible dans le dossier du projet

</div>

