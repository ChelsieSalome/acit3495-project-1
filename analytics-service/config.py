import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MySQL Connection (connects to your existing MySQL container)
    MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
    MYSQL_USER = os.getenv("MYSQL_USER", "user") 
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "project1")
    
    # MongoDB Connection (connects to your MongoDB service)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
    MONGO_DB = os.getenv("MONGO_DB", "analytics_db")
    ANALYTICS_COLLECTION = os.getenv("ANALYTICS_COLLECTION", "analytics_results")
    
    # Flask Settings
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5004))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
