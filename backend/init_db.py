import sqlite3
from pathlib import Path

# 确定数据库文件路径
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "journal.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journals (
        journal_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL CHECK (side IN ('buy', 'sell')),
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        note TEXT,
        exit_price REAL,
        exit_time TIMESTAMP,
        pnl REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    conn.commit()
    conn.close()

    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
