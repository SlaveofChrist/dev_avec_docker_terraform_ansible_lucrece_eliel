import os
import psycopg2
import redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

app = FastAPI()

# Configuration CORS pour autoriser le Frontend JS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod, on mettrait l'URL précise du frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration via Variables d'Environnement
PG_HOST = os.getenv("POSTGRES_HOST", "db")
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "password")
PG_DB = os.getenv("POSTGRES_DB", "ynov_ci")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

def get_db_connection():
    """Crée une connexion propre à la DB."""
    return psycopg2.connect(
        host=PG_HOST,
        user=PG_USER,
        password=PG_PASS,
        database=PG_DB
    )

@app.get("/")
async def get_students():
    results = []
    conn = None
    try:
        # 1. Récupération des données froides (Postgres)
        conn = get_db_connection()
        cur = conn.cursor()
        # On suppose que la table 'students' a été créée par le script SQL
        cur.execute("SELECT id, nom, promo FROM students ORDER BY id;")
        rows = cur.fetchall()
        
        # 2. Connexion au Cache (Redis)
        # On le fait ici pour gérer l'indisponibilité potentielle
        r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True, socket_connect_timeout=1)
        redis_available = True
        try:
            r.ping() # Vérifie si Redis répond vraiment
        except redis.exceptions.ConnectionError:
            print("⚠️ AVERTISSEMENT : Redis est indisponible. Mode dégradé activé.")
            redis_available = False

        # 3. Construction de la réponse (Fusion Données + Cache)
        for row in rows:
            student_id = row[0]
            nom = row[1]
            promo = row[2]
            
            views = 0
            # Logique de comptage Redis
            if redis_available:
                try:
                    key = f"student:{student_id}:views"
                    views = r.incr(key) # Incrémente et retourne la nouvelle valeur
                except redis.exceptions.RedisError:
                    views = 0 # Fallback si erreur pendant l'incrément
            
            results.append({
                "id": student_id,
                "nom": nom,
                "promo": promo,
                "views": views
            })
            
    except Exception as e:
        print(f"❌ Erreur critique : {e}")
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

    return results