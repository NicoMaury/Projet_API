from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Optional

app = FastAPI(title="Rail Traffic API")

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
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None

@app.get("/")
def read_root():
    return {"message": "Welcome to the Rail Traffic API"}

@app.get("/departements")
def get_departements():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT nom FROM departements ORDER BY nom;")
        departements = cur.fetchall()
        cur.close()
        conn.close()
        return [d['nom'] for d in departements]
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gares")
def get_gares(limit: int = 100, offset: int = 0, departement: Optional[str] = None):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        query = "SELECT * FROM gares"
        params = []
        
        if departement:
            query += " WHERE departement = %s"
            params.append(departement)
            
        query += " ORDER BY libelle LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cur.execute(query, tuple(params))
        gares = cur.fetchall()
        cur.close()
        conn.close()
        return gares
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
