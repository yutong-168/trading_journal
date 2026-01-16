from app.repos.journal_repo import (
    create_journal, get_journals_by_user, get_journal_by_id, update_journal, 
    delete_journal, update_journal_pnl, get_journals, get_stats_summary_by_user
    )
from datetime import datetime

def add_journal(user_id, symbol, side, price, quantity, note=None):
    if side not in ("buy", "sell"):
        raise ValueError("Invalid side, must be 'buy' or 'sell'")
    
    if price <= 0:
        raise ValueError("Price must be positive")
    
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    
    if note is not None and len(note) > 1000:
        raise ValueError("Note is too long")

    journal_id = create_journal(
        user_id=user_id,
        symbol=symbol,
        side=side,
        price=price,
        quantity=quantity,
        note=note,
    )
    
    return journal_id


def list_journals(user_id):
    return get_journals_by_user(user_id)


def update_journal_by_id(user_id, journal_id, symbol, side, price, quantity, note=None):
    journal = get_journal_by_id(journal_id)
    
    if journal is None:
        raise ValueError("Journal not found")
    
    journal_user_id = journal[1]
    if journal_user_id != user_id:
        raise PermissionError("You do not have permission to update this journal")
    
    if side not in ("buy", "sell"):
        raise ValueError("Invalid side, must be 'buy' or 'sell'")
    
    if price <= 0:
        raise ValueError("Price must be positive")
    
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    
    if note is not None and len(note) > 1000:
        raise ValueError("Note is too long")
    
    update_journal(
        journal_id=journal_id,
        symbol=symbol,
        side=side,
        price=price,
        quantity=quantity,
        note=note,
    )
    
    return True


def delete_journal_by_id(user_id, journal_id):
    journal = get_journal_by_id(journal_id)
    
    if journal is None:
        raise ValueError("Journal not found")
    
    journal_user_id = journal[1]
    if journal_user_id != user_id:
        raise PermissionError("You do not have permission to update this journal")
    
    delete_journal(journal_id)


def close_trade_by_id(user_id, journal_id, exit_price):
    journal = get_journal_by_id(journal_id)

    if journal is None:
        raise ValueError("Journal not found")

    journal_user_id = journal[1]
    side = journal[3]
    entry_price = journal[4]
    quantity = journal[5]
    existing_exit_price = journal[7]

    if journal_user_id != user_id:
        raise PermissionError("No permission to close this journal")

    if existing_exit_price is not None:
        raise ValueError("Trade already closed")

    if exit_price <= 0:
        raise ValueError("Exit price must be positive")

    if side == "buy":
        pnl = (exit_price - entry_price) * quantity
    else:
        pnl = (entry_price - exit_price) * quantity

    update_journal_pnl(
        journal_id=journal_id,
        exit_price=exit_price,
        pnl=pnl
    )

    return pnl


def list_journals_filtered(
    user_id,
    symbol=None,
    status=None,
    start_date=None,
    end_date=None,
    side=None,
):
    # 轻量参数校验
    if side is not None and side not in ("buy", "sell"):
        raise ValueError("Invalid side, must be 'buy' or 'sell'")

    if status is not None and status not in ("open", "closed"):
        raise ValueError("Invalid status, must be 'open' or 'closed'")

    # 校验日期格式 YYYY-MM-DD，并检查范围合法
    def _validate_date_str(date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            raise ValueError("Invalid date format, expected YYYY-MM-DD")

    if start_date:
        _validate_date_str(start_date)
    if end_date:
        _validate_date_str(end_date)
    if start_date and end_date:
        if start_date > end_date:
            raise ValueError("start_date must be <= end_date")

    return get_journals(
        user_id=user_id,
        symbol=symbol,
        status=status,
        start_date=start_date,
        end_date=end_date,
        side=side,
    )


def stats_summary(user_id: int):
    row = get_stats_summary_by_user(user_id)
    if row is None:
        return {
            "closed_trades": 0,
            "open_trades": 0,
            "total_pnl": 0,
            "win_rate": 0,
            "avg_win": 0,
            "avg_loss": 0,
        }

    closed_trades, open_trades, total_pnl, win_trades, loss_trades, avg_win, avg_loss = row

    closed_trades = closed_trades or 0
    open_trades = open_trades or 0
    total_pnl = float(total_pnl or 0)
    win_trades = win_trades or 0
    avg_win = float(avg_win or 0)
    avg_loss = float(avg_loss or 0)

    win_rate = (win_trades / closed_trades) if closed_trades > 0 else 0

    return {
        "closed_trades": closed_trades,
        "open_trades": open_trades,
        "total_pnl": total_pnl,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
    }
