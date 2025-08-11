from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Load config
    from app.config import Config
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Configure Flask-Login
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"


    # Import models so SQLAlchemy is aware of them
    with app.app_context():
        from . import models

    # Make a global `now()` available in all templates
    @app.context_processor
    def inject_now():
        return {"now": lambda: datetime.now()}

    # Import and register blueprints
    from app.routes import main, auth, booking, facility
    app.register_blueprint(main.main)
    app.register_blueprint(auth.bp)
    app.register_blueprint(booking.bp)
    app.register_blueprint(facility.bp)

    return app
