import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB  = os.getenv("MONGO_DB", "analytics_db")

    # Flask
    FLASK_PORT  = int(os.getenv("FLASK_PORT", 5003))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"

    # Collection names — defined once, used everywhere
    ANALYTICS_COLLECTION = "analytics_results"
