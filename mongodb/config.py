import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Settings
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "analytics_db")
    ANALYTICS_COLLECTION = "analytics_results"

    # MySQL Settings 
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "project1")

    # Flask Settings
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5004))  
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"