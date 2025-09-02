import os
import certifi
from dotenv import load_dotenv

load_dotenv()

ENV = os.environ.get("FLASK_ENV", "dev").lower()

class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")
    # This is the root path where all uploaded media (blog, companies, etc.) will live
    MEDIA_ROOT = os.path.join("static", "media")
    UPLOAD_FOLDER = os.path.join("static", "media")  # ✅ Add this line

class Config(BaseConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
    MONGO_URI = os.environ.get("MONGO_URI")
    MONGO_CERT = certifi.where()

class TestConfig(Config):
    # No hardcoded path; env controls it. Optional fallback to local sqlite.
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///atllocal.db")

class DevConfig(Config):
    # Purely env-driven; no defaults to avoid leaking or accidental use
    SQLALCHEMY_DATABASE_URI = os.environ["DEV_DATABASE_URL"]

class ProdConfig(Config):
    # Purely env-driven; no defaults
    SQLALCHEMY_DATABASE_URI = os.environ["PROD_DATABASE_URL"]

# Select active config
if ENV == "test":
    ActiveConfig = TestConfig
elif ENV == "prod":
    ActiveConfig = ProdConfig
else:
    ActiveConfig = DevConfig
