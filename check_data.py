import psycopg2
import os

# Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "rail_traffic_db")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None

def print_data(conn):
    cur = conn.cursor()
    
    print("\n--- STATISTIQUES ---")
    # Count Departements
    cur.execute("SELECT COUNT(*) FROM departements;")
    count_dept = cur.fetchone()[0]
    print(f"Nombre de départements: {count_dept}")
    
    # Count Gares
    cur.execute("SELECT COUNT(*) FROM gares;")
    count_gares = cur.fetchone()[0]
    print(f"Nombre de gares: {count_gares}")
    
    print("\n--- EXEMPLE DE DONNÉES (5 premières gares) ---")
    cur.execute("""
        SELECT code_uic, libelle, commune, departement 
        FROM gares 
        ORDER BY libelle 
        LIMIT 5;
    """)
    rows = cur.fetchall()
    for row in rows:
        print(f"Gare: {row[1]} ({row[0]}) - Commune: {row[2]} - Dept: {row[3]}")

    cur.close()

if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        print_data(conn)
        conn.close()
