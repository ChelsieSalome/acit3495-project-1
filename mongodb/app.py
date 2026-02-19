# app.py - COMPLETE ANALYTICS SERVICE
from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
from pymongo import MongoClient
from datetime import datetime, timezone
import logging
from config import Config
from models import analytics_document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Database connections
mongo_client = MongoClient(Config.MONGO_URI)
mongo_db = mongo_client[Config.MONGO_DB]
analytics_collection = mongo_db[Config.ANALYTICS_COLLECTION]

def get_mysql_connection():
    """Create MySQL connection"""
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )

def get_highest_selling_product():
    """Query MySQL to get the highest selling product"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT 
            p.Product_id as product_id,
            p.Product_name as product_name,
            SUM(s.Quantity) as total_quantity_sold
        FROM Products p
        JOIN Sale s ON p.Product_id = s.Product_id
        GROUP BY p.Product_id, p.Product_name
        ORDER BY total_quantity_sold DESC
        LIMIT 1
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting highest selling product: {e}")
        return None

def get_top_customer():
    """Query MySQL to get the customer with highest purchase value"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT 
            c.Customer_id as customer_id,
            c.Customer_name as customer_name,
            SUM(s.Quantity * p.Product_price) as total_purchase_value
        FROM Customer c
        JOIN Sale s ON c.Customer_id = s.Customer_id
        JOIN Products p ON s.Product_id = p.Product_id
        GROUP BY c.Customer_id, c.Customer_name
        ORDER BY total_purchase_value DESC
        LIMIT 1
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting top customer: {e}")
        return None

def store_analytics_results(highest_selling_product, top_customer):
    """Store analytics results in MongoDB"""
    try:
        # Create document using your models.py function
        document = analytics_document(highest_selling_product, top_customer)
        
        # Use upsert to replace existing "latest" document
        result = analytics_collection.replace_one(
            {"type": "latest"},  # filter
            document,            # replacement document
            upsert=True          # create if doesn't exist
        )
        
        logger.info(f"Analytics results stored successfully. Upserted: {result.upserted_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error storing data in MongoDB: {e}")
        return False

#  ROUTES 
@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "service": "analytics-service", 
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

@app.route("/run-analytics", methods=["POST"])
def run_analytics():
    """
    Main analytics endpoint:
    1. Queries MySQL for analytics data
    2. Computes highest selling product and top customer
    3. Stores results in MongoDB
    """
    try:
        logger.info("Starting analytics calculation...")
        
        # Get analytics data from MySQL
        highest_selling_product = get_highest_selling_product()
        top_customer = get_top_customer()
        
        if not highest_selling_product or not top_customer:
            return jsonify({
                "error": "Unable to retrieve analytics data from MySQL"
            }), 500
        
        # Store results in MongoDB
        if store_analytics_results(highest_selling_product, top_customer):
            logger.info("Analytics completed successfully")
            
            return jsonify({
                "message": "Analytics completed successfully",
                "results": {
                    "highest_selling_product": highest_selling_product,
                    "top_customer": top_customer
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }), 200
        else:
            return jsonify({
                "error": "Failed to store analytics results"
            }), 500
            
    except Exception as e:
        logger.error(f"Error in analytics calculation: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/analytics-status", methods=["GET"])
def get_analytics_status():
    """
    Returns the latest analytics results from MongoDB.
    Called by external services to get computed results.
    """
    try:
        result = analytics_collection.find_one(
            {"type": "latest"},
            {"_id": 0}  # exclude MongoDB's internal _id field
        )

        if result is None:
            return jsonify({
                "message": "No analytics data available yet. Run /run-analytics first."
            }), 404

        # Convert datetime to string for JSON serialization
        if "timestamp" in result:
            result["timestamp"] = result["timestamp"].isoformat()

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error retrieving analytics status: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )
