import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "journal.db"

def create_journal(user_id, symbol, side, price, quantity, note=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO journals (user_id, symbol, side, price, quantity, note)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, symbol, side, price, quantity, note)
    )
    
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id


def get_journals_by_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT
            journal_id,
            symbol,
            side,
            price,
            quantity,
            exit_price,
            pnl,
            note,
            created_at
        FROM journals
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,)
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows


def get_journal_by_id(journal_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            journal_id,
            user_id,
            symbol,
            side,
            price,
            quantity,
            note,
            exit_price,
            exit_time,
            pnl,
            created_at
        FROM journals
        WHERE journal_id = ?
        """,
        (journal_id,)
    )

    row = cursor.fetchone()
    conn.close()

    return row



def update_journal(journal_id, symbol, side, price, quantity, note):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE journals
        SET symbol = ?,
            side = ?,
            price = ?,
            quantity = ?,
            note = ?
        WHERE journal_id = ?
        """,
        (symbol, side, price, quantity, note, journal_id)
    )

    conn.commit()
    conn.close()


def delete_journal(journal_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        DELETE FROM journals
        WHERE journal_id = ?
        """,
        (journal_id,)
    )
    
    conn.commit()
    conn.close()

def update_journal_pnl(journal_id, exit_price, pnl):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE journals
        SET exit_price = ?,
            exit_time = CURRENT_TIMESTAMP,
            pnl = ?
        WHERE journal_id = ?
        """,
        (exit_price, pnl, journal_id)
    )

    conn.commit()
    conn.close()


def get_journals(
    user_id,
    symbol=None,
    status=None,      # "open" or "closed"
    start_date=None,  # "YYYY-MM-DD"
    end_date=None,    # "YYYY-MM-DD"
    side=None,
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sql = """
        SELECT journal_id, user_id, symbol, side, price, quantity, note,
               exit_price, exit_time, pnl, created_at
        FROM journals
        WHERE user_id = ?
    """
    params = [user_id]

    # 1) symbol filter
    if symbol:
        sql += " AND symbol = ?"
        params.append(symbol)

    # 2) side filter
    if side:
        sql += " AND side = ?"
        params.append(side)

    # 3) status filter
    if status == "open":
        sql += " AND exit_time IS NULL"
    elif status == "closed":
        sql += " AND exit_time IS NOT NULL"
    elif status is not None:
        conn.close()
        raise ValueError("Invalid status, must be 'open' or 'closed'")

    # 4) date range filter (created_at)
    if start_date:
        sql += " AND date(created_at) >= date(?)"
        params.append(start_date)

    if end_date:
        sql += " AND date(created_at) <= date(?)"
        params.append(end_date)

    sql += " ORDER BY created_at DESC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_stats_summary_by_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            -- counts
            SUM(CASE WHEN exit_time IS NOT NULL THEN 1 ELSE 0 END) AS closed_trades,
            SUM(CASE WHEN exit_time IS NULL THEN 1 ELSE 0 END) AS open_trades,

            -- pnl aggregates (only closed)
            COALESCE(SUM(CASE WHEN exit_time IS NOT NULL THEN pnl ELSE 0 END), 0) AS total_pnl,

            -- win/loss breakdown (only closed)
            SUM(CASE WHEN exit_time IS NOT NULL AND pnl > 0 THEN 1 ELSE 0 END) AS win_trades,
            SUM(CASE WHEN exit_time IS NOT NULL AND pnl < 0 THEN 1 ELSE 0 END) AS loss_trades,

            COALESCE(AVG(CASE WHEN exit_time IS NOT NULL AND pnl > 0 THEN pnl END), 0) AS avg_win,
            COALESCE(AVG(CASE WHEN exit_time IS NOT NULL AND pnl < 0 THEN pnl END), 0) AS avg_loss
        FROM journals
        WHERE user_id = ?
        """,
        (user_id,),
    )

    row = cursor.fetchone()
    conn.close()

    return row
