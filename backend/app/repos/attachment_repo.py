import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple

# Derive backend/ path: this file is backend/app/repos/attachment_repo.py
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "journal.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

AttachmentRow = Tuple[int, int, int, str, str, str, int, Optional[int], Optional[int], str]

def insert_attachment(
    journal_id: int,
    user_id: int,
    storage_key: str,
    public_url: str,
    mime: str,
    size: int,
    width: int = None,
    height: int = None,
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO attachments (journal_id, user_id, storage_key, public_url, mime, size, width, height)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (journal_id, user_id, storage_key, public_url, mime, size, width, height),
    )
    conn.commit()
    attachment_id = cursor.lastrowid
    conn.close()
    return attachment_id

def list_attachments_by_journal(journal_id: int) -> List[AttachmentRow]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT attachment_id, journal_id, user_id, storage_key, public_url,
               mime, size, width, height, created_at
        FROM attachments
        WHERE journal_id = ?
        ORDER BY attachment_id DESC
        """,
        (journal_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_attachment(attachment_id: int) -> Optional[AttachmentRow]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT attachment_id, journal_id, user_id, storage_key, public_url,
               mime, size, width, height, created_at
        FROM attachments
        WHERE attachment_id = ?
        """,
        (attachment_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return row

def delete_attachment(attachment_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attachments WHERE attachment_id = ?", (attachment_id,))
    conn.commit()
    conn.close()

