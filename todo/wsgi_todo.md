# To-Do: wsgi.py

- [ ] Verify that the WSGI entry point matches the correct Flask app instance.
- [ ] Ensure the app import path is correct for the deployment environment.
- [ ] Review production settings (e.g., debug mode is disabled).
- [ ] Confirm compatibility with chosen server (Gunicorn, uWSGI, etc.).
- [ ] Add minimal logging for startup errors to aid debugging in production.
- [ ] If using environment variables, ensure `.env` is loaded before app import.
