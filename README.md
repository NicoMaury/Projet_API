# 🚆 Rail Traffic Analytics

> **API REST sophistiquée pour l'analyse et le suivi du trafic ferroviaire français en temps réel**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat&logo=postgresql)](https://www.postgresql.org/)
[![Keycloak](https://img.shields.io/badge/Keycloak-23.0-4D4D4D?style=flat&logo=keycloak)](https://www.keycloak.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker)](https://www.docker.com/)

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

### Structure du Projet

```
Projet_API/
├── app/
│   ├── api/
│   │   └── routes/          # 12 endpoints REST
│   │       ├── alerts.py    # Alertes majeures
│   │       ├── departements.py
│   │       ├── lines.py     # Lignes ferroviaires
│   │       ├── regions.py
│   │       ├── stations.py  # Gares SNCF
│   │       ├── stats.py     # Statistiques globales
│   │       └── trains.py    # Trains en circulation
│   ├── core/
│   │   ├── config.py        # Configuration Pydantic
│   │   ├── database.py      # SQLAlchemy
│   │   ├── rate_limit.py    # SlowAPI
│   │   └── security.py      # Validation JWT
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
./start-docker.sh

# 2. Installer les dépendances Python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configurer l'environnement
cp .env.example .env
nano .env  # Éditer avec les URLs Docker

# 4. Démarrer l'API
fastapi dev app/main.py
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

### Obtenir un token

```bash
curl -X POST 'http://localhost:8080/realms/rail/protocol/openid-connect/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'client_id=rail-traffic-api' \
  -d 'client_secret=VOTRE_SECRET' \
  -d 'grant_type=password' \
  -d 'username=testuser' \
  -d 'password=password'
```

### Utiliser le token

```bash
export TOKEN="votre_access_token"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/stations
```

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
./start-docker.sh

# Arrêter Docker
docker-compose down

# Activer l'environnement Python
source .venv/bin/activate

# Démarrer l'API en mode développement
fastapi dev app/main.py

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

[Documentation](API_ENDPOINTS.md) • [Guide Docker](DOCKER_GUIDE.md) • [Installation](GUIDE_INSTALLATION.md)

</div>

