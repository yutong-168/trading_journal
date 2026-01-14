from flask import Flask
from app.routes.health import health_bp
from app.routes.auth import auth_bp
from app.routes.journal import journal_bp
from app.routes.stats import stats_bp

def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(stats_bp)
    
    return app
