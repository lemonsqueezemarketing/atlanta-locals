from flask import Flask
from config import Config 
from .models import db

def create_app(run_db_create=False):
    app = Flask(__name__, static_folder='static', template_folder='templates')  
    app.config.from_object(Config)

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    if run_db_create:
        with app.app_context():
            db.create_all()

    return app