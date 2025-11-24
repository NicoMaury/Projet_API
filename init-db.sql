-- Script d'initialisation PostgreSQL
-- Créé automatiquement au démarrage du conteneur

-- Se connecter à la base rail_analytics
\c rail_analytics

-- ============================================================================
-- TABLE: request_logs (logs d'API)
-- ============================================================================
CREATE TABLE IF NOT EXISTS request_logs (
    id SERIAL PRIMARY KEY,
    method VARCHAR(10) NOT NULL,
    path VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    status_code INTEGER NOT NULL,
    duration_ms INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_request_logs_user_id ON request_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_request_logs_created_at ON request_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_request_logs_status_code ON request_logs(status_code);

-- ============================================================================
-- TABLE: regions (Régions françaises)
-- ============================================================================
CREATE TABLE IF NOT EXISTS regions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    nom VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_regions_code ON regions(code);
CREATE INDEX IF NOT EXISTS idx_regions_nom ON regions(nom);

-- ============================================================================
-- TABLE: departements (Départements français)
-- ============================================================================
CREATE TABLE IF NOT EXISTS departements (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    nom VARCHAR(255) NOT NULL,
    region_code VARCHAR(10) REFERENCES regions(code) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_departements_code ON departements(code);
CREATE INDEX IF NOT EXISTS idx_departements_nom ON departements(nom);
CREATE INDEX IF NOT EXISTS idx_departements_region ON departements(region_code);

-- ============================================================================
-- TABLE: stations (Gares SNCF)
-- ============================================================================
CREATE TABLE IF NOT EXISTS stations (
    id SERIAL PRIMARY KEY,
    uic_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    commune VARCHAR(255),
    departement_code VARCHAR(100),  -- Removed FK: API returns names not codes
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    is_active BOOLEAN DEFAULT TRUE,
    has_freight BOOLEAN DEFAULT FALSE,
    has_passengers BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_stations_uic_code ON stations(uic_code);
CREATE INDEX IF NOT EXISTS idx_stations_name ON stations(name);
CREATE INDEX IF NOT EXISTS idx_stations_departement ON stations(departement_code);
CREATE INDEX IF NOT EXISTS idx_stations_active ON stations(is_active);

-- ============================================================================
-- TABLE: lines (Lignes ferroviaires)
-- ============================================================================
CREATE TABLE IF NOT EXISTS lines (
    id SERIAL PRIMARY KEY,
    line_code VARCHAR(200) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    network VARCHAR(100),
    color VARCHAR(7),
    text_color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_lines_code ON lines(line_code);
CREATE INDEX IF NOT EXISTS idx_lines_name ON lines(name);
CREATE INDEX IF NOT EXISTS idx_lines_active ON lines(is_active);

-- ============================================================================
-- TABLE: trains (Trains en circulation)
-- ============================================================================
CREATE TABLE IF NOT EXISTS trains (
    id SERIAL PRIMARY KEY,
    train_number VARCHAR(50) NOT NULL,
    line_code VARCHAR(200) REFERENCES lines(line_code) ON DELETE SET NULL,
    origin VARCHAR(255),
    destination VARCHAR(255),
    departure_time TIMESTAMP WITH TIME ZONE,
    arrival_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50),
    delay_minutes INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_trains_number ON trains(train_number);
CREATE INDEX IF NOT EXISTS idx_trains_line ON trains(line_code);
CREATE INDEX IF NOT EXISTS idx_trains_status ON trains(status);
CREATE INDEX IF NOT EXISTS idx_trains_departure ON trains(departure_time);

-- ============================================================================
-- NOTE: Incidents/Disruptions are fetched directly from Navitia API in real-time
-- No database storage needed for incidents
-- ============================================================================
-- TABLE: station_delay_stats (Statistiques de retards par gare)
-- ============================================================================
CREATE TABLE IF NOT EXISTS station_delay_stats (
    id SERIAL PRIMARY KEY,
    station_uic_code VARCHAR(20) REFERENCES stations(uic_code) ON DELETE CASCADE,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    total_trains INTEGER DEFAULT 0,
    delayed_trains INTEGER DEFAULT 0,
    average_delay_minutes DOUBLE PRECISION DEFAULT 0.0,
    max_delay_minutes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_station_delay_stats_station ON station_delay_stats(station_uic_code);
CREATE INDEX IF NOT EXISTS idx_station_delay_stats_date ON station_delay_stats(date);

-- ============================================================================
-- TABLE: line_stats (Statistiques de performance par ligne)
-- ============================================================================
CREATE TABLE IF NOT EXISTS line_stats (
    id SERIAL PRIMARY KEY,
    line_code VARCHAR(200) REFERENCES lines(line_code) ON DELETE CASCADE,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    total_trains INTEGER DEFAULT 0,
    on_time_trains INTEGER DEFAULT 0,
    delayed_trains INTEGER DEFAULT 0,
    cancelled_trains INTEGER DEFAULT 0,
    punctuality_rate DOUBLE PRECISION DEFAULT 0.0,
    average_delay_minutes DOUBLE PRECISION DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_line_stats_line ON line_stats(line_code);
CREATE INDEX IF NOT EXISTS idx_line_stats_date ON line_stats(date);

-- ============================================================================
-- MESSAGE DE CONFIRMATION
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '====================================================';
    RAISE NOTICE 'Base de données rail_analytics initialisée !';
    RAISE NOTICE 'Tables créées : ';
    RAISE NOTICE '  - request_logs';
    RAISE NOTICE '  - regions';
    RAISE NOTICE '  - departements';
    RAISE NOTICE '  - stations';
    RAISE NOTICE '  - lines';
    RAISE NOTICE '  - trains';
    RAISE NOTICE '  - incidents';
    RAISE NOTICE '  - station_delay_stats';
    RAISE NOTICE '  - line_stats';
    RAISE NOTICE '====================================================';
END $$;

