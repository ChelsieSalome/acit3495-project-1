from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
from pymongo import MongoClient
from config import Config
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#  Database Connections 
def get_mysql_connection():
    """Create MySQL connection"""
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )

def get_mongodb_connection():
    """Create MongoDB connection"""
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DB]
    return db[Config.ANALYTICS_COLLECTION]

#  Analytics Functions 

def get_highest_selling_product():
    """Find the product with highest total quantity sold"""
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
        
        return result if result else {
            "product_id": None,
            "product_name": "No sales data",
            "total_quantity_sold": 0
        }
        
    except Exception as e:
        logger.error(f"Error getting highest selling product: {e}")
        return {
            "product_id": None,
            "product_name": "Error retrieving data",
            "total_quantity_sold": 0
        }

def get_top_customer():
    """Find the customer with highest total purchase value"""
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
        
        if result:
            # Convert Decimal to float for JSON serialization
            result['total_purchase_value'] = float(result['total_purchase_value'])
            return result
        else:
            return {
                "customer_id": None,
                "customer_name": "No customer data",
                "total_purchase_value": 0.0
            }
        
    except Exception as e:
        logger.error(f"Error getting top customer: {e}")
        return {
            "customer_id": None,
            "customer_name": "Error retrieving data",
            "total_purchase_value": 0.0
        }

def store_analytics_in_mongodb(highest_selling_product, top_customer):
    """Store analytics results in MongoDB"""
    try:
        collection = get_mongodb_connection()
        
        # Create analytics document
        analytics_doc = {
            "type": "latest",
            "timestamp": datetime.utcnow(),
            "highest_selling_product": highest_selling_product,
            "top_customer": top_customer
        }
        
        # Replace existing "latest" document (upsert)
        collection.replace_one(
            {"type": "latest"}, 
            analytics_doc, 
            upsert=True
        )
        
        logger.info("Analytics data stored in MongoDB successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error storing data in MongoDB: {e}")
        return False

#  Routes 

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok", 
        "service": "analytics-service",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route("/run-analytics", methods=["POST"])
def run_analytics():
    """
    Trigger analytics calculation:
    1. Query MySQL for insights
    2. Store results in MongoDB
    """
    try:
        logger.info("Starting analytics calculation...")
        
        # Get analytics data from MySQL
        highest_selling_product = get_highest_selling_product()
        top_customer = get_top_customer()
        
        # Store results in MongoDB
        success = store_analytics_in_mongodb(highest_selling_product, top_customer)
        
        if success:
            return jsonify({
                "message": "Analytics completed successfully",
                "results": {
                    "highest_selling_product": highest_selling_product,
                    "top_customer": top_customer
                },
                "timestamp": datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                "error": "Failed to store analytics in MongoDB"
            }), 500
            
    except Exception as e:
        logger.error(f"Analytics calculation failed: {e}")
        return jsonify({
            "error": f"Analytics calculation failed: {str(e)}"
        }), 500

@app.route("/analytics-status", methods=["GET"])
def analytics_status():
    """Get current analytics data from MongoDB"""
    try:
        collection = get_mongodb_connection()
        result = collection.find_one(
            {"type": "latest"},
            {"_id": 0}
        )
        
        if result:
            # Convert datetime to string for JSON serialization
            if "timestamp" in result:
                result["timestamp"] = result["timestamp"].isoformat()
            return jsonify(result), 200
        else:
            return jsonify({
                "message": "No analytics data available. Run /run-analytics first."
            }), 404
            
    except Exception as e:
        logger.error(f"Error retrieving analytics status: {e}")
        return jsonify({
            "error": f"Failed to retrieve analytics: {str(e)}"
        }), 500

#  Entry Point 
if __name__ == "__main__":
    logger.info(f"Starting Analytics Service on port {Config.FLASK_PORT}")
    app.run(
        host="0.0.0.0",
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )
