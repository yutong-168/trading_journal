from pathlib import Path
import sys

# Support direct execution: `python3 app/run.py` from `backend/`.
if __package__ in (None, ""):
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
