web: gunicorn app:app
release: python -c "from app import create_app, init_db; app = create_app(); app.app_context().push(); print('Database initialized')"
