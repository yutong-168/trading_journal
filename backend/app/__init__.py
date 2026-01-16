from flask import Flask
from flask_cors import CORS
from app.routes.health import health_bp
from app.routes.auth import auth_bp
from app.routes.journal import journal_bp
from app.routes.stats import stats_bp
from app.routes.attachments import attachments_bp
from flask import send_from_directory
from pathlib import Path

def create_app():
    app = Flask(__name__)

    # Allow frontend (Vite) to call the API during development.
    # Adjust origins if you use a different dev port or hostname.
    CORS(
        app,
        resources={r"/*": {"origins": [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ]}},
        supports_credentials=True,
    )

    # Configure local uploads directory and static serving
    BASE_DIR = Path(__file__).resolve().parents[1]
    uploads_dir = BASE_DIR / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    app.config["UPLOADS_DIR"] = str(uploads_dir)

    @app.route("/uploads/<path:filename>")
    def serve_uploads(filename: str):
        return send_from_directory(app.config["UPLOADS_DIR"], filename)

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(attachments_bp)
    
    return app
