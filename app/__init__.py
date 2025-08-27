# app/__init__.py

from flask import Flask
from config import ActiveConfig
from .models import db, MyUser  # import MyUser for user_loader

# Mongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Flask-Login
from flask_login import LoginManager


def create_app(run_db_create: bool = False, drop_db_all: bool = False):
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(ActiveConfig)
    print(f"[init] Loaded config: {ActiveConfig.__name__}")

    # Ensure SECRET_KEY exists (needed for sessions/flash/login)
    if not app.config.get("SECRET_KEY"):
        # Fail fast in prod, fall back only in dev/test
        if ActiveConfig is not None and ActiveConfig.__name__ == "ProdConfig":
            raise RuntimeError("SECRET_KEY is not set for production.")
        app.config["SECRET_KEY"] = "dev1"

    # --- SQLAlchemy (PostgreSQL/SQLite) ---
    db.init_app(app)

    # --- MongoDB (Atlas) ---
    try:
        app.mongo_client = MongoClient(
            app.config.get("MONGO_URI"),
            server_api=ServerApi("1"),
            tlsCAFile=app.config.get("MONGO_CERT"),
        )
        app.mongo_db = app.mongo_client[app.config.get("MONGO_DBNAME", "atlLocal")]
        app.mongo_client.admin.command("ping")
        print("✅ MongoDB connected (app.mongo_db ready)")
    except Exception as e:
        app.mongo_client = None
        app.mongo_db = None
        print(f"❌ MongoDB connection error at init: {e}")

    # --- Blueprints ---
    from .routes import main
    app.register_blueprint(main)

    from .api import api_bp
    app.register_blueprint(api_bp)

    # --- DB helpers ---
    if run_db_create:
        with app.app_context():
            db.create_all()
    if drop_db_all:
        with app.app_context():
            db.drop_all()

    # --- Flask-Login setup ---
    login_manager = LoginManager()
    login_manager.login_view = "main.login"  # your login route inside 'main' blueprint
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return MyUser.query.get(int(user_id))

    return app
