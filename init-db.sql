-- Script d'initialisation PostgreSQL
-- Créé automatiquement au démarrage du conteneur

-- Créer la base de données Keycloak
SELECT 'CREATE DATABASE keycloak'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'keycloak')\gexec

-- Créer l'utilisateur Keycloak
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE rolname = 'keycloak_user') THEN
      CREATE USER keycloak_user WITH PASSWORD 'keycloak_password';
   END IF;
END
$do$;

-- Donner les privilèges
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak_user;

-- Se connecter à la base rail_analytics
\c rail_analytics

-- Créer la table request_logs si elle n'existe pas
CREATE TABLE IF NOT EXISTS request_logs (
    id SERIAL PRIMARY KEY,
    method VARCHAR(10) NOT NULL,
    path VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    status_code INTEGER NOT NULL,
    duration_ms INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Créer des index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_request_logs_user_id ON request_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_request_logs_created_at ON request_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_request_logs_status_code ON request_logs(status_code);

-- Afficher un message de confirmation
DO $$
BEGIN
    RAISE NOTICE 'Base de données rail_analytics initialisée avec succès!';
END $$;

