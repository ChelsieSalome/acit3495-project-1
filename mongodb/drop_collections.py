from pymongo import MongoClient
from config import Config

def drop_collections():
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DB]

    existing_collections = db.list_collection_names()

    if Config.ANALYTICS_COLLECTION in existing_collections:
        db[Config.ANALYTICS_COLLECTION].drop()
        print(f"Collection '{Config.ANALYTICS_COLLECTION}' dropped.")
    else:
        print(f"Collection '{Config.ANALYTICS_COLLECTION}' does not exist.")

    client.close()
    print("Done.")

if __name__ == "__main__":
    confirm = input("This will delete all data. Type 'yes' to confirm: ")
    if confirm.lower() == "yes":
        drop_collections()
    else:
        print("Cancelled.")
