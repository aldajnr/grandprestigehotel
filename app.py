import os
from flask import Flask
from config import Config
from models.db import get_db, close_db
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.guest_routes import guest_bp
from routes.audit_routes import audit_bp
from routes.admin_routes import admin_bp
from models.user_model import get_user_by_username, create_user


def init_db(app):
    with app.app_context():
        db = get_db()
        schema_path = os.path.join(os.path.dirname(__file__), "database", "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            db.executescript(f.read())
        db.commit()
        for col_sql in [
            "ALTER TABLE guests ADD COLUMN status TEXT NOT NULL DEFAULT 'active'",
            "ALTER TABLE guests ADD COLUMN cancelled_by INTEGER",
            "ALTER TABLE guests ADD COLUMN cancel_reason TEXT",
        ]:
            try:
                db.execute(col_sql)
                db.commit()
            except Exception:
                pass


def seed_users(app):
    """Single admin account only. All other staff created via Admin panel."""
    with app.app_context():
        db = get_db()
        for old in ["admin@zetech.ac.ke", "manager@zetech.ac.ke", "reception@zetech.ac.ke"]:
            db.execute("DELETE FROM users WHERE username=?", (old,))
        db.commit()
        if not get_user_by_username("kaharukakelvin@zetech.ac.ke"):
            create_user("kaharukakelvin@zetech.ac.ke", "kaharuka", "Admin")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(os.path.join(os.path.dirname(__file__), "instance"), exist_ok=True)
    init_db(app)
    seed_users(app)
    app.teardown_appcontext(close_db)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(guest_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(admin_bp)
    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(debug=debug, host="0.0.0.0", port=port)
