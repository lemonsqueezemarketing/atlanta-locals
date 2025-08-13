import os
import certifi

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Environment flags
ENV = os.environ.get("FLASK_ENV", "dev").lower()  # defaults to dev if not set

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MongoDB configuration
    MONGO_DBNAME = "atlLocal"
    MONGO_URI = (
        "mongodb+srv://lemonsqueezemarketing:"
        "yBiTYxe3rgrFIqXU"
        "@cluster0.vv0bfam.mongodb.net/atlLocal"
        "?retryWrites=true&w=majority&appName=Cluster0"
    )
    MONGO_CERT = certifi.where()


class TestConfig(Config):
    # SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'atllocal.db')


class DevConfig(Config):
    # Local PostgreSQL for development
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres%40W2025@localhost:5432/postgres"


# Pick config based on ENV
if ENV == "test":
    ActiveConfig = TestConfig
elif ENV == "dev":
    ActiveConfig = DevConfig
else:
    ActiveConfig = DevConfig  # default to dev for now
