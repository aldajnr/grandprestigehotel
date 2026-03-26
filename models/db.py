"""
Database connection helper.
Tries MySQL first (via PyMySQL); falls back to SQLite if MySQL is
not configured or unavailable.
"""

import sqlite3
from flask import current_app, g

try:
    import pymysql
    import pymysql.cursors
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False


def _use_mysql(app) -> bool:
    return (
        PYMYSQL_AVAILABLE
        and bool(app.config.get("MYSQL_USER"))
        and bool(app.config.get("MYSQL_DB"))
    )


def get_db():
    if "db" not in g:
        if _use_mysql(current_app):
            conn = pymysql.connect(
                host=current_app.config["MYSQL_HOST"],
                port=current_app.config["MYSQL_PORT"],
                user=current_app.config["MYSQL_USER"],
                password=current_app.config["MYSQL_PASSWORD"],
                database=current_app.config["MYSQL_DB"],
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
            )
            g.db_type = "mysql"
        else:
            conn = sqlite3.connect(current_app.config.get("SQLITE_PATH") or current_app.config["DB_PATH"])
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            g.db_type = "sqlite"
        g.db = conn
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def is_mysql() -> bool:
    return g.get("db_type") == "mysql"


def execute(sql: str, params: tuple = ()):
    db = get_db()
    if is_mysql():
        sql = sql.replace("?", "%s")
        cur = db.cursor()
        cur.execute(sql, params)
        return cur
    else:
        return db.execute(sql, params)


def fetchall(sql: str, params: tuple = ()) -> list:
    cur = execute(sql, params)
    rows = cur.fetchall()
    if is_mysql():
        return rows
    return [dict(r) for r in rows]


def fetchone(sql: str, params: tuple = ()):
    cur = execute(sql, params)
    row = cur.fetchone()
    if row is None:
        return None
    if is_mysql():
        return row
    return dict(row)


def commit():
    get_db().commit()
