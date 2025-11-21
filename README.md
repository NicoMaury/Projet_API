# Rail Traffic Analytics

## Aperçu
Rail Traffic Analytics est une API FastAPI sécurisée destinée à analyser les flux ferroviaires
français. Elle s'intègre à Keycloak pour l'authentification OpenID Connect, applique un
rate-limiting utilisateur avec SlowAPI et prépare les services tiers nécessaires pour interroger le
dataset open data SNCF « liste-des-gares ».

## Fonctionnalités clés
- **Authentification** : validation stricte des JWT Keycloak (signature, audience, issuer, exp).
- **Rate limiting** : 100 requêtes/minute/utilisateur via SlowAPI en se basant sur l'identité
  (`sub`).
- **Architecture modulaire** : routes, services, modèles et configuration isolés pour faciliter la
  maintenance.
- **Intégrations externes** : clients HTTP prêts pour le dataset SNCF « liste-des-gares » et les
  autres jeux open data SNCF.
- **Prise en charge des environnements** : configuration typée via Pydantic avec `.env` et exemple
  fourni.
- **Persistance SQL** : journalisation automatique de chaque requête HTTP dans PostgreSQL (table
  `request_logs`).

## Arborescence principale
```
app/
├── api/
│   └── routes/        # Placeholders protégés pour toutes les routes demandées
├── core/              # Configuration, sécurité Keycloak, rate limiting
├── models/            # Schémas Pydantic partagés
├── services/          # Clients dataset SNCF et OpenData
└── main.py            # Création de l'application FastAPI
```

## Démarrage rapide
1. **Configurer l'environnement**
   ```bash
   cp .env.example .env
   # éditer les valeurs Keycloak/OpenData/PostgreSQL
   ```
2. **Créer l'environnement virtuel et installer les dépendances**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows : .venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. **Lancer l'API**
   ```bash
   fastapi run app/main.py --reload
   ```

## Variables d'environnement essentielles
- `KEYCLOAK_JWKS_URL` : URL JWKS du realm Keycloak.
- `KEYCLOAK_AUDIENCE` : client_id attendu dans le token.
- `KEYCLOAK_ISSUER` : issuer exact (ex. `https://kc.example.com/realms/rail`).
- `SNCF_DATASET_URL` : URL complète du dataset « liste-des-gares » (limit, filtres, etc.).
- `OPENDATA_API_KEY` : clé d’API open data SNCF (facultatif selon les jeux de données).
- `REQUEST_TIMEOUT_SECONDS` : timeout HTTP global pour les services externes.
- `DATABASE_URL` : DSN SQLAlchemy PostgreSQL
  (`postgresql+psycopg://user:password@host:5432/base`).

## Utilisation
1. **Keycloak** : créez un client `confidential` et récupérez l'URL JWKS, l'issuer et le
   `client_id` (audience). Les accès API requièrent un `access_token` signé RS256.
2. **Base PostgreSQL** : créez la base cible et mettez à jour `DATABASE_URL`. L'application crée la
   table `request_logs` au démarrage.
3. **Lancement** : démarrez `fastapi run app/main.py --reload` puis appelez une route avec un token
   valide.

Exemple de requête (token fictif) :

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/stations
```

Chaque appel exécute les vérifications suivantes :

- Validation du JWT contre Keycloak (signature, audience, issuer, expiration).
- Application du rate limiting utilisateur (100 req/minute).
- Insertion d'une ligne dans `request_logs` avec la route appelée, l'utilisateur (claim `sub`), le
  statut HTTP et la durée.

## Persistance PostgreSQL
- **Table créée** : `request_logs` (colonnes `id`, `method`, `path`, `user_id`, `status_code`,
  `duration_ms`, `created_at`).
- **Fonctionnement** : un middleware FastAPI mesure la durée d'exécution, puis insère la ligne via
  SQLAlchemy après chaque réponse HTTP.
- **Exploration** : connectez-vous à PostgreSQL et exécutez par exemple :

```sql
SELECT method, path, user_id, status_code, duration_ms, created_at
FROM request_logs
ORDER BY created_at DESC
LIMIT 20;
```

## Sécurité et bonnes pratiques
- Toutes les routes exigent un JWT Keycloak valide via la dépendance `require_keycloak_token`.
- Les charges utiles validées sont stockées dans `request.state.token_payload` pour un accès
  applicatif.
- SlowAPI bloque automatiquement les clients qui dépassent 100 requêtes/minute et renvoie un HTTP
  429.

## Prochaines étapes
- Implémenter la logique métier dans chaque route en utilisant `stations_dataset_service` et
  `opendata_service`.
- Ajouter des tests automatiques pour couvrir les intégrations principales et la sécurité.
