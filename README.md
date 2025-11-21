# 🚆 Rail Traffic Analytics

> **API REST sophistiquée pour l'analyse et le suivi du trafic ferroviaire français SNCF en temps réel**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat&logo=postgresql)](https://www.postgresql.org/)
[![Keycloak](https://img.shields.io/badge/Keycloak-23.0-4D4D4D?style=flat&logo=keycloak)](https://www.keycloak.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker)](https://www.docker.com/)

---

## 🎯 Fonctionnalités Principales

| Fonctionnalité | Description |
|----------------|-------------|
| 🚄 **Temps Réel** | Suivi des trains, retards et suppressions en direct |
| 🗺️ **Réseau Complet** | 6000+ gares, toutes les lignes SNCF |
| 📊 **Statistiques** | Analyses détaillées par ligne et par gare |
| ⚠️ **Alertes** | Détection et historique des incidents majeurs |
| 🔒 **Sécurisé** | OAuth2 avec Keycloak + Rate limiting (100 req/min) |
| 🐘 **PostgreSQL** | Base de données robuste et performante |

---

## ⚡ Démarrage Ultra Rapide

### Prérequis

- **Python 3.10+**
- **Docker & Docker Compose**
- **Git**

### Installation en 5 étapes

```bash
# 1️⃣ Cloner le projet
git clone <votre-repo-url>
cd Projet_API

# 2️⃣ Démarrer PostgreSQL et Keycloak
docker compose up -d

# 3. Créer l'environnement virtuel Python
python3 -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Configurer Keycloak automatiquement
python setup_keycloak.py

# 6. Lancer l'API (synchronisation automatique des données)
python start.py
```

> **⚠️ Important** : Tous les scripts Python (`setup_keycloak.py`, `get_token.py`, `start.py`, etc.) doivent être lancés avec l'environnement virtuel activé (`source .venv/bin/activate`).

**🎉 C'est prêt !** Ouvrez http://localhost:8000/docs

---

## 📊 Vérifier les Données Synchronisées

Après le démarrage, l'API charge automatiquement :

```bash
# Test rapide de synchronisation
python test_sync.py
```

**Résultat attendu :**
```
✅ 13 régions synchronisées
✅ 5 départements synchronisés
✅ 6000+ gares synchronisées
✅ 25+ lignes synchronisées
✅ 120+ trains synchronisés
✅ 25+ alertes synchronisées
```

---

## 🔑 Authentification OAuth2

### Obtenir un token rapidement

```bash
# Méthode 1 : Script automatique
python get_token.py

# Méthode 2 : Commande manuelle
curl -X POST 'http://localhost:8080/realms/rail/protocol/openid-connect/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'client_id=rail-traffic-api' \
  -d 'client_secret=<voir .keycloak_secret>' \
  -d 'grant_type=password' \
  -d 'username=testuser' \
  -d 'password=password'
```

### Utiliser le token

```bash
export TOKEN="votre_access_token"

# Tester l'API
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/regions
```

### Interface Swagger UI

1. Ouvrir http://localhost:8000/docs
2. Cliquer sur le bouton **"Authorize"** 🔒
3. Coller le token
4. Tester les endpoints directement !

📖 **Guide complet** : [KEYCLOAK_GUIDE.md](KEYCLOAK_GUIDE.md)

---

## 📡 Endpoints de l'API

### 📍 Géolocalisation

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/regions` | Liste toutes les régions françaises |
| `GET` | `/regions/{id}` | Détails d'une région |
| `GET` | `/departements` | Liste tous les départements |
| `GET` | `/departements/{id}` | Détails d'un département |

### 🚉 Gares & Stations

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/stations` | Liste des gares (pagination) |
| `GET` | `/stations/{code_uic}` | Détails d'une gare |
| `GET` | `/stations/{code_uic}/delays` | Statistiques de retards |
| `GET` | `/stations/search?q=Paris` | Recherche de gares |

### 🚆 Lignes & Trains

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/lines` | Liste des lignes ferroviaires |
| `GET` | `/lines/{id}` | Détails d'une ligne |
| `GET` | `/lines/{id}/stats` | Performance d'une ligne |
| `GET` | `/trains` | Trains en circulation |
| `GET` | `/trains/{id}` | Détails d'un train |

### ⚠️ Alertes & Incidents

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/alerts` | Toutes les alertes actives |
| `GET` | `/alerts/major` | Alertes critiques uniquement |
| `GET` | `/alerts/{id}` | Détails d'une alerte |

### 📊 Statistiques

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/stats/delays/top` | Top 10 des gares les plus en retard |
| `GET` | `/stats/lines/punctuality` | Taux de ponctualité par ligne |

📚 **Documentation interactive complète** : http://localhost:8000/docs

---

## 🏗️ Architecture Technique

### Stack Technologique

```
┌─────────────────────────────────────┐
│     FastAPI + Uvicorn (API)         │
├─────────────────────────────────────┤
│  Keycloak (OAuth2 / OpenID Connect) │
├─────────────────────────────────────┤
│    PostgreSQL 15 (Base de données)  │
├─────────────────────────────────────┤
│   Sources de données externes :     │
│  • Navitia.io (temps réel)          │
│  • SNCF Open Data (horaires)        │
│  • OpenDataSoft (référentiels)      │
└─────────────────────────────────────┘
```

### Structure du Projet

```
Projet_API/
├── app/
│   ├── api/routes/         # Endpoints de l'API
│   ├── core/               # Configuration, sécurité, DB
│   ├── models/             # Modèles SQLAlchemy
│   ├── services/           # Intégrations APIs externes
│   └── tasks/              # Synchronisation des données
├── docker-compose.yml      # Services (PostgreSQL, Keycloak)
├── start.py                # Point d'entrée principal
├── setup_keycloak.py       # Configuration auto Keycloak
├── get_token.py            # Récupération rapide de token
└── test_sync.py            # Test de synchronisation
```

---

## ⚙️ Configuration

### Variables d'environnement (.env)

```env
# API
API_TITLE=Rail Traffic Analytics
API_VERSION=0.1.0

# PostgreSQL
DATABASE_URL=postgresql+psycopg://rail_user:rail_password@localhost:5432/rail_analytics

# Keycloak OAuth2
KEYCLOAK_JWKS_URL=http://localhost:8080/realms/rail/protocol/openid-connect/certs
KEYCLOAK_AUDIENCE=rail-traffic-api
KEYCLOAK_ISSUER=http://localhost:8080/realms/rail

# APIs externes
NAVITIA_API_KEY=your_navitia_api_key
OPENDATA_API_BASE_URL=https://data.sncf.com/api/explore/v2.1
OPENDATASOFT_BASE_URL=https://public.opendatasoft.com/api/explore/v2.1
```

📝 **Note** : Copiez `.env.example` vers `.env` et ajustez les valeurs.

---

## 🗄️ Base de Données

### Accès à PostgreSQL

**Via pgAdmin (inclus)** : http://localhost:5050
- Email : `admin@rail.local`
- Password : `admin`

**Via DataGrip / DBeaver :**
- Host : `localhost`
- Port : `5432`
- Database : `rail_analytics`
- User : `rail_user`
- Password : `rail_password`

### Tables principales

| Table | Description | Lignes (après sync) |
|-------|-------------|---------------------|
| `regions` | Régions françaises | ~13 |
| `departements` | Départements | ~5 |
| `stations` | Gares SNCF | ~6000 |
| `lines` | Lignes ferroviaires | ~25 |
| `trains` | Trains en circulation | ~120 |
| `alerts` | Alertes et incidents | ~25 |
| `request_logs` | Logs des requêtes API | Variable |

### Requêtes SQL utiles

```sql
-- Top 10 des gares avec le plus de trains
SELECT name, COUNT(*) as train_count
FROM trains t
JOIN stations s ON t.station_id = s.id
GROUP BY s.name
ORDER BY train_count DESC
LIMIT 10;

-- Alertes critiques actives
SELECT title, severity, affected_lines
FROM alerts
WHERE status = 'active' AND severity = 'critical';

-- Taux de ponctualité par ligne
SELECT line_external_id,
       AVG(CASE WHEN delay_minutes = 0 THEN 100 ELSE 0 END) as punctuality_rate
FROM trains
GROUP BY line_external_id;
```

---

## 🧪 Tests

### Tester la synchronisation

```bash
python test_sync.py
```

### Tester les APIs

```bash
# Sans authentification (mode dev)
python test_apis.py

# Avec authentification
export TOKEN=$(./get_token.sh | grep export | cut -d'"' -f2)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/stations?limit=5
```

---

## 🐳 Docker

### Commandes utiles

```bash
# Démarrer tous les services
docker compose up -d

# Voir les logs
docker compose logs -f

# Arrêter les services
docker compose down

# Réinitialiser complètement (⚠️ supprime les données)
docker compose down -v
docker compose up -d
./setup_keycloak.sh
```

### Services disponibles

| Service | Port | URL |
|---------|------|-----|
| **API FastAPI** | 8000 | http://localhost:8000 |
| **Swagger UI** | 8000 | http://localhost:8000/docs |
| **PostgreSQL** | 5432 | `psql -h localhost -U rail_user -d rail_analytics` |
| **pgAdmin** | 5050 | http://localhost:5050 |
| **Keycloak** | 8080 | http://localhost:8080 |

---

## 🔒 Sécurité

### Rate Limiting

- **Limite** : 100 requêtes par minute par utilisateur
- **Identification** : Token OAuth2 (sub claim)
- **Réponse** : HTTP 429 si dépassé

### OAuth2 / OpenID Connect

- **Protocole** : OAuth2 avec Keycloak
- **Flux** : Resource Owner Password Credentials Grant
- **Token** : JWT signé RS256
- **Durée** : 5 minutes (configurable)

### Bonnes pratiques

- ✅ `.env` dans `.gitignore`
- ✅ Client secrets jamais dans le code
- ✅ HTTPS obligatoire en production
- ✅ Rotation régulière des secrets

---

## 🚀 Déploiement Production

### Checklist

- [ ] Variables d'environnement en secrets
- [ ] `KC_HOSTNAME` configuré pour Keycloak
- [ ] HTTPS activé (Let's Encrypt, Traefik, Nginx)
- [ ] PostgreSQL avec backup automatique
- [ ] Monitoring (Prometheus, Grafana)
- [ ] Rate limiting ajusté selon le traffic
- [ ] Logs centralisés (ELK, Loki)

### Exemple avec Docker Compose (production)

```yaml
services:
  api:
    image: ghcr.io/votre-org/rail-traffic-api:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - KEYCLOAK_ISSUER=https://auth.votredomaine.com/realms/rail
    restart: always
    depends_on:
      - postgres
      - keycloak
```

---

## 📖 Documentation Complète

- **[KEYCLOAK_GUIDE.md](KEYCLOAK_GUIDE.md)** - Configuration Keycloak pas à pas
- **[API Documentation](http://localhost:8000/docs)** - Swagger UI interactive
- **[ReDoc](http://localhost:8000/redoc)** - Documentation alternative

---

## 🛠️ Développement

### Installer en mode dev

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Si vous avez des outils de dev
```

### Lancer en mode développement

```bash
# Avec rechargement automatique
python start.py

# Ou directement avec uvicorn
uvicorn app.main:app --reload
```

### Pré-commit hooks

```bash
# Installer pre-commit
pip install pre-commit
pre-commit install

# Lancer manuellement
pre-commit run --all-files
```

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Merci de :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Commit vos changements (`git commit -m 'Ajout fonctionnalité X'`)
4. Push vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrir une Pull Request

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- **SNCF Open Data** - Données ouvertes ferroviaires
- **Navitia.io** - API de transport en temps réel
- **OpenDataSoft** - Référentiels géographiques
- **Keycloak** - Solution d'authentification open-source
- **FastAPI** - Framework web moderne et performant

---

## 📞 Support

- 📧 Email : support@votredomaine.com
- 🐛 Issues : [GitHub Issues](https://github.com/votre-org/Projet_API/issues)
- 💬 Discord : [Rejoindre la communauté](#)

---

**🚆 Happy Tracking! 🚄**

