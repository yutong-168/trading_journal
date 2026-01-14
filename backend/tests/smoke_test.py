import json
import sys
from pathlib import Path
from datetime import datetime

# Ensure we run from backend/ so that 'app' package is resolvable
CURRENT_FILE = Path(__file__).resolve()
BACKEND_DIR = CURRENT_FILE.parents[1]
if Path.cwd() != BACKEND_DIR:
    print(f"Please run this script from: {BACKEND_DIR}")
    sys.exit(2)

# Ensure backend directory is on sys.path for module resolution
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Initialize database schema (idempotent)
import init_db  # noqa: E402
init_db.init_db()

from app import create_app  # noqa: E402


def assert_status(resp, expected_codes, label):
    if isinstance(expected_codes, int):
        expected_codes = [expected_codes]
    if resp.status_code not in expected_codes:
        print(f"[FAIL] {label}: expected {expected_codes}, got {resp.status_code}, body={resp.get_data(as_text=True)}")
        sys.exit(1)
    print(f"[OK] {label}: {resp.status_code}")


def main():
    app = create_app()
    client = app.test_client()

    # Health
    r = client.get("/")
    assert_status(r, 200, "health")
    print("health body:", r.get_data(as_text=True).strip())

    # Register user (allow exists)
    test_email = "smoke_user@example.com"
    test_password = "smoke_pass_123"

    r = client.post("/auth/register", json={"email": test_email, "password": test_password})
    assert_status(r, [200, 409], "auth.register")
    print("register body:", r.get_data(as_text=True).strip())

    # Login to get user_id
    r = client.post("/auth/login", json={"email": test_email, "password": test_password})
    assert_status(r, 200, "auth.login")
    login_data = r.get_json()
    print("login body:", json.dumps(login_data, ensure_ascii=False))
    user_id = login_data["user_id"]

    # Create journal
    payload = {
        "user_id": user_id,
        "symbol": "AAPL",
        "side": "buy",
        "price": 123.45,
        "quantity": 10,
        "note": "smoke create",
    }
    r = client.post("/journals", json=payload)
    assert_status(r, 201, "journals.create")
    print("create body:", r.get_data(as_text=True).strip())

    # List journals
    r = client.get(f"/journals?user_id={user_id}")
    assert_status(r, 200, "journals.list")
    journals = r.get_json()
    print("list body:", json.dumps(journals, ensure_ascii=False))
    assert len(journals) >= 1, "Expected at least one journal entry"

    journal_id = journals[0]["journal_id"]

    # Stats summary (basic contract check)
    r = client.get(f"/stats/summary?user_id={user_id}")
    assert_status(r, 200, "stats.summary")
    summary = r.get_json()
    print("summary body:", json.dumps(summary, ensure_ascii=False))
    # Basic keys and types
    for key in ["closed_trades", "open_trades", "total_pnl", "win_rate", "avg_win", "avg_loss"]:
        assert key in summary, f"Missing key in summary: {key}"
    assert isinstance(summary["closed_trades"], int), "closed_trades should be int"
    assert isinstance(summary["open_trades"], int), "open_trades should be int"
    assert isinstance(summary["total_pnl"], (int, float)), "total_pnl should be number"
    assert isinstance(summary["win_rate"], (int, float)), "win_rate should be number"
    assert isinstance(summary["avg_win"], (int, float)), "avg_win should be number"
    assert isinstance(summary["avg_loss"], (int, float)), "avg_loss should be number"
    assert 0 <= summary["win_rate"] <= 1, "win_rate should be in [0,1]"

    # List journals with filters
    today = datetime.now().strftime("%Y-%m-%d")
    filter_qs = (
        f"/journals?user_id={user_id}"
        f"&symbol=AAPL"
        f"&side=buy"
        f"&status=open"
        f"&start_date={today}"
        f"&end_date={today}"
    )
    r = client.get(filter_qs)
    assert_status(r, 200, "journals.list.filtered")
    filtered = r.get_json()
    print("filtered list body:", json.dumps(filtered, ensure_ascii=False))
    assert len(filtered) >= 1, "Expected at least one filtered journal entry"
    for item in filtered:
        assert item["symbol"] == "AAPL", "Filter by symbol failed"
        assert item["side"] == "buy", "Filter by side failed"

    # Update journal
    update_payload = {
        "user_id": user_id,
        "symbol": "AAPL",
        "side": "buy",
        "price": 130.0,
        "quantity": 12,
        "note": "smoke update",
    }
    r = client.put(f"/journals/{journal_id}", json=update_payload)
    assert_status(r, 200, "journals.update")
    print("update body:", r.get_data(as_text=True).strip())

    # Delete journal
    r = client.delete(f"/journals/{journal_id}", json={"user_id": user_id})
    assert_status(r, 200, "journals.delete")
    print("delete body:", r.get_data(as_text=True).strip())

    print("[SUCCESS] Smoke tests finished successfully.")


if __name__ == "__main__":
    main()
