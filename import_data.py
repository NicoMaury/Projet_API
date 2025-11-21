import requests
import psycopg2
import time
import os

# Configuration
API_URL = "https://data.sncf.com/api/explore/v2.1/catalog/datasets/liste-des-gares/records"
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "rail_traffic_db")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

def get_db_connection():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("Connected to database.")
            return conn
        except psycopg2.OperationalError as e:
            print(f"Waiting for database... Error: {e}")
            time.sleep(2)

def create_tables(conn):
    cur = conn.cursor()
    
    # Table Departements
    cur.execute("""
        CREATE TABLE IF NOT EXISTS departements (
            nom VARCHAR(255) PRIMARY KEY
        );
    """)
    
    # Table Gares
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gares (
            code_uic VARCHAR(20) PRIMARY KEY,
            libelle VARCHAR(255),
            fret VARCHAR(5),
            voyageurs VARCHAR(5),
            code_ligne VARCHAR(20),
            rg_troncon INTEGER,
            pk VARCHAR(20),
            commune VARCHAR(255),
            departement VARCHAR(255),
            idreseau INTEGER,
            idgaia VARCHAR(50),
            x_l93 FLOAT,
            y_l93 FLOAT,
            x_wgs84 FLOAT,
            y_wgs84 FLOAT,
            longitude FLOAT,
            latitude FLOAT,
            FOREIGN KEY (departement) REFERENCES departements(nom)
        );
    """)
    
    conn.commit()
    cur.close()
    print("Tables created.")

def fetch_and_insert_data(conn):
    cur = conn.cursor()
    limit = 100
    offset = 0
    total_count = 1 # Initialize to enter loop
    
    while offset < total_count:
        print(f"Fetching records with offset {offset}...")
        params = {
            "limit": limit,
            "offset": offset
        }
        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            total_count = data.get("total_count", 0)
            results = data.get("results", [])
            
            if not results:
                break
                
            for record in results:
                # Insert Departement if not exists
                dept = record.get("departemen")
                if dept:
                    cur.execute("""
                        INSERT INTO departements (nom) VALUES (%s)
                        ON CONFLICT (nom) DO NOTHING;
                    """, (dept,))
                
                # Prepare Gare data
                code_uic = record.get("code_uic")
                if not code_uic:
                    continue # Skip if no ID
                    
                geo_point = record.get("geo_point_2d", {})
                if geo_point is None:
                    geo_point = {}
                
                cur.execute("""
                    INSERT INTO gares (
                        code_uic, libelle, fret, voyageurs, code_ligne, rg_troncon, pk,
                        commune, departement, idreseau, idgaia, x_l93, y_l93, x_wgs84, y_wgs84,
                        longitude, latitude
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (code_uic) DO UPDATE SET
                        libelle = EXCLUDED.libelle,
                        fret = EXCLUDED.fret,
                        voyageurs = EXCLUDED.voyageurs,
                        commune = EXCLUDED.commune,
                        departement = EXCLUDED.departement,
                        longitude = EXCLUDED.longitude,
                        latitude = EXCLUDED.latitude;
                """, (
                    code_uic,
                    record.get("libelle"),
                    record.get("fret"),
                    record.get("voyageurs"),
                    record.get("code_ligne"),
                    record.get("rg_troncon"),
                    record.get("pk"),
                    record.get("commune"),
                    dept,
                    record.get("idreseau"),
                    record.get("idgaia"),
                    record.get("x_l93"),
                    record.get("y_l93"),
                    record.get("x_wgs84"),
                    record.get("y_wgs84"),
                    geo_point.get("lon"),
                    geo_point.get("lat")
                ))
            
            conn.commit()
            offset += limit
            
        except Exception as e:
            print(f"Error processing batch: {e}")
            break

    cur.close()
    print("Import completed.")

if __name__ == "__main__":
    conn = get_db_connection()
    create_tables(conn)
    fetch_and_insert_data(conn)
    conn.close()
