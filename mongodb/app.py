from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from config import Config


CORS(app) 


app = Flask(__name__)

#  MongoDB Connection 
client = MongoClient(Config.MONGO_URI)
db = client[Config.MONGO_DB]
collection = db[Config.ANALYTICS_COLLECTION]

# Routes 

@app.route("/health", methods=["GET"])
def health():
    """Health check — confirms the service is running."""
    return jsonify({"status": "ok", "service": "mongodb-service"}), 200


@app.route("/analytics", methods=["GET"])
def get_analytics():
    """
    Returns the latest analytics result from MongoDB.
    Called by the Show Results Web App.
    """
    try:
        result = collection.find_one(
            {"type": "latest"},
            {"_id": 0}          # exclude MongoDB's internal _id field
        )

        if result is None:
            return jsonify({
                "message": "No analytics data available yet."
            }), 404

        # Convert datetime to string for JSON serialization
        if "timestamp" in result:
            result["timestamp"] = result["timestamp"].isoformat()

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#  Entry Point 
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )
