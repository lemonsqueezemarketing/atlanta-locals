# app/__init__.py

from flask import Flask
from config import ActiveConfig
from .models import db

# Mongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def create_app(run_db_create=False, drop_db_all=False):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(ActiveConfig)
    print(f"[init] Loaded config: {ActiveConfig.__name__}")

    # --- SQLAlchemy (PostgreSQL/SQLite) ---
    db.init_app(app)

    # --- MongoDB (Atlas) ---
    # Create a single client for the whole app; reuse across requests
    try:
        app.mongo_client = MongoClient(
            ActiveConfig.MONGO_URI,
            server_api=ServerApi("1"),
            tlsCAFile=getattr(ActiveConfig, "MONGO_CERT", None),
        )
        # Choose default database (e.g., 'atlLocal')
        app.mongo_db = app.mongo_client[getattr(ActiveConfig, "MONGO_DBNAME", "atlLocal")]

        # Quick health check (optional; remove if too noisy)
        app.mongo_client.admin.command("ping")
        print("✅ MongoDB connected (app.mongo_db ready)")
    except Exception as e:
        # Do not crash app on startup; log and allow later retries if desired
        app.mongo_client = None
        app.mongo_db = None
        print(f"❌ MongoDB connection error at init: {e}")

    # --- Blueprints ---
    from .routes import main
    app.register_blueprint(main)

    # API v1 blueprint
    from .api import api_bp
    app.register_blueprint(api_bp)

    # --- Optional DB helpers for local dev ---
    if run_db_create:
        with app.app_context():
            db.create_all()
    if drop_db_all:
        with app.app_context():
            db.drop_all()

    # --- Graceful shutdown for Mongo client ---
    # @app.teardown_appcontext
    # def _close_mongo_client(exception=None):
    #     client = getattr(app, "mongo_client", None)
    #     if client is not None:
    #         # MongoClient is thread-safe; closing here is optional.
    #         # If you prefer to keep it for the whole process lifetime, you can remove this.
    #         client.close()

    return app

