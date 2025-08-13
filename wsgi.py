# wsgi.py  (project root, next to main.py)
from app import create_app

# Export both common names
app = create_app()
application = app
