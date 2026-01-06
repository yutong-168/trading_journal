import sqlite3
from pathlib import Path

# current at backend [2] /app [1] /repos [0] /user_repo.py
# parents[2] get us back to backend/
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "journal.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_user_by_email(email: str):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT user_id, email, password_hash, created_at FROM users WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    conn.close()
    
    return row

def create_user(email: str, password_hash: str):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (email, password_hash)
    )
    conn.commit()
    conn.close()