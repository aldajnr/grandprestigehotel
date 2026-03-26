import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "zetech-hotel-2025-secure-key")
    
    # Database configuration — supports both SQLite and MySQL
    # For production on Render, set DATABASE_URL environment variable
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    if DATABASE_URL.startswith("mysql://"):
        # Parse MySQL URL (mysql://user:pass@host:port/dbname)
        db_url = DATABASE_URL.replace("mysql://", "").replace("mysql+pymysql://", "")
        parts = db_url.split("@")
        user_pass = parts[0].split(":")
        host_port_db = parts[1].split("/")
        host_port = host_port_db[0].split(":")
        
        MYSQL_USER = user_pass[0]
        MYSQL_PASSWORD = user_pass[1] if len(user_pass) > 1 else ""
        MYSQL_HOST = host_port[0]
        MYSQL_PORT = int(host_port[1]) if len(host_port) > 1 else 3306
        MYSQL_DB = host_port_db[1]
    else:
        # Default to SQLite
        DB_PATH = os.path.join(BASE_DIR, "instance", "hotel.db")
        MYSQL_USER = ""
        MYSQL_PASSWORD = ""
        MYSQL_HOST = ""
        MYSQL_PORT = 3306
        MYSQL_DB = ""

    MAIL_SERVER   = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT     = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    # Default MAIL_FROM to MAIL_USERNAME — Gmail rejects mismatched From headers
    MAIL_FROM     = os.environ.get("MAIL_FROM") or os.environ.get("MAIL_USERNAME", "noreply@grandhotel.com")
    MAIL_ENABLED  = bool(os.environ.get("MAIL_USERNAME", ""))
    OTP_EXPIRY_SEC = 300
