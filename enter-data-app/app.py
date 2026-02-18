from flask import Flask, request, render_template_string
import mysql.connector

app = Flask(__name__)

db_config = {
    "host": "mysql",
    "user": "user",
    "password": "password",
    "database": "project1"
}

# -------------------------
# CUSTOMER FORM (existing)
# -------------------------
customer_form = '''
<form method="POST">
  Name: <input name="name"><br>
  Email: <input name="email"><br>
  <input type="submit" value="Submit">
</form>
'''

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Customer (Customer_name, Email) VALUES (%s, %s)",
            (name, email)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return "Customer added!"
    return render_template_string(customer_form)


# -------------------------
# PRODUCT FORM
# -------------------------
product_form = '''
<form method="POST">
  Product Name: <input name="product_name"><br>
  Price: <input name="price" type="number" step="0.01"><br>
  <input type="submit" value="Submit">
</form>
'''

@app.route("/product", methods=["GET", "POST"])
def product():
    if request.method == "POST":
        product_name = request.form["product_name"]
        price = request.form["price"]
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Products (Product_name, Product_price) VALUES (%s, %s)",
            (product_name, price)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return "Product added!"
    return render_template_string(product_form)


# -------------------------
# SALE FORM
# -------------------------
sale_form = '''
<form method="POST">
  Customer ID: <input name="customer_id" type="number"><br>
  Product ID: <input name="product_id" type="number"><br>
  Quantity: <input name="quantity" type="number"><br>
  <input type="submit" value="Submit">
</form>
'''

@app.route("/sale", methods=["GET", "POST"])
def sale():
    if request.method == "POST":
        customer_id = request.form["customer_id"]
        product_id = request.form["product_id"]
        quantity = request.form["quantity"]
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Sale (Customer_id, Product_id, Quantity) VALUES (%s, %s, %s)",
            (customer_id, product_id, quantity)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return "Sale recorded!"
    return render_template_string(sale_form)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)