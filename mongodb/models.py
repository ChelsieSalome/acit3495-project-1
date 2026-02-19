from datetime import datetime

def analytics_document(highest_selling_product: dict, top_customer: dict) -> dict:
    """
    Defines the structure of an analytics result document in MongoDB.

    Example document stored in 'analytics_results' collection:
    {
        "type": "latest",
        "timestamp": "2026-02-18T12:00:00",
        "highest_selling_product": {
            "product_id": 1,
            "product_name": "Widget A",
            "total_quantity_sold": 500
        },
        "top_customer": {
            "customer_id": 3,
            "customer_name": "Jane Doe",
            "total_purchase_value": 9999.99
        }
    }
    """
    return {
        "type": "latest",
        "timestamp": datetime.utcnow(),
        "highest_selling_product": {
            "product_id":           highest_selling_product.get("product_id"),
            "product_name":         highest_selling_product.get("product_name"),
            "total_quantity_sold":  highest_selling_product.get("total_quantity_sold"),
        },
        "top_customer": {
            "customer_id":           top_customer.get("customer_id"),
            "customer_name":         top_customer.get("customer_name"),
            "total_purchase_value":  top_customer.get("total_purchase_value"),
        }
    }