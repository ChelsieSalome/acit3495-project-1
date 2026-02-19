import os


class Config:
    # ── MySQL ──────────────────────────────────────────────────────────────────
    MYSQL_HOST          = os.environ.get("MYSQL_HOST",          "mysql-db")
    MYSQL_PORT          = os.environ.get("MYSQL_PORT",          "3307")
    MYSQL_USER          = os.environ.get("MYSQL_USER",          "user")
    MYSQL_PASSWORD      = os.environ.get("MYSQL_PASSWORD",      "password")
    MYSQL_DATABASE      = os.environ.get("MYSQL_DATABASE",      "project1")

    # ── MongoDB ────────────────────────────────────────────────────────────────
    MONGO_URI            = os.environ.get("MONGO_URI",          "mongodb://mongodb:27017")
    MONGO_DB             = os.environ.get("MONGO_DB",           "analytics_db")
    ANALYTICS_COLLECTION = os.environ.get("ANALYTICS_COLLECTION", "analytics")

    # ── Flask ──────────────────────────────────────────────────────────────────
    FLASK_PORT  = int(os.environ.get("ANALYTICS_SERVICE_PORT",  5004))
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
