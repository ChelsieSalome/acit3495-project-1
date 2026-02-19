import sys
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

# Import config (make sure config.py exists)
try:
    from config import Config
except ImportError:
    print("config.py not found. Create it first!")
    sys.exit(1)

def create_collections():
    try:
        print(f"Connecting to MongoDB: {Config.MONGO_URI}")

        # Add timeout to prevent hanging
        client = MongoClient(
            Config.MONGO_URI,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )

        # Test connection immediately
        client.server_info()
        print("MongoDB connection successful!")

        db = client[Config.MONGO_DB]

        #  Create analytics_results collection
        existing_collections = db.list_collection_names()
        print(f"Existing collections: {existing_collections}")

        if Config.ANALYTICS_COLLECTION not in existing_collections:
            db.create_collection(Config.ANALYTICS_COLLECTION)
            print(f"Collection '{Config.ANALYTICS_COLLECTION}' created.")
        else:
            print(f"Collection '{Config.ANALYTICS_COLLECTION}' already exists.")

        #  Create index on 'type' field for fast lookups
        collection = db[Config.ANALYTICS_COLLECTION]

        try:
            collection.create_index([("type", ASCENDING)], unique=True)
            print("Index on 'type' created.")
        except Exception as e:
            if "already exists" in str(e):
                print("Index on 'type' already exists.")
            else:
                print(f"Index creation warning: {e}")

        client.close()
        print("MongoDB setup complete.")

    except ServerSelectionTimeoutError:
        print("MongoDB connection failed: Server not reachable")
        print("Solutions:")
        print("   1. Start MongoDB: docker run -d --name mongodb -p 27017:27017 mongo")
        print("   2. Check if MongoDB service is running")
        print("   3. Verify connection string in config.py")
        sys.exit(1)

    except ConnectionFailure:
        print("MongoDB connection failed: Connection refused")
        print("MongoDB server is not running")
        sys.exit(1)

    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"Error type: {type(e).__name__}")
        sys.exit(1)

if __name__ == "__main__":
    create_collections()