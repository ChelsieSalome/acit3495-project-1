from flask import Flask, request, render_template_string, redirect, url_for, make_response
import mysql.connector
import requests
import os
from datetime import date

app = Flask(__name__)

db_config = {
    "host": os.environ.get("MYSQL_HOST", "mysql"),
    "user": os.environ.get("MYSQL_USER", "user"),
    "password": os.environ.get("MYSQL_PASSWORD", "password"),
    "database": os.environ.get("MYSQL_DATABASE", "project1")
}

AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth-service:5001")
TOKEN_COOKIE_NAME = "auth_token"


# -------------------------
# Auth helpers
# -------------------------
def verify_token(token: str) -> bool:
    if not token:
        return False
    try:
        r = requests.get(
            f"{AUTH_SERVICE_URL}/verify",
            headers={"Authorization": f"Bearer {token}"},
            timeout=3
        )
        return r.status_code == 200
    except requests.RequestException:
        return False

def require_auth():
    token = request.cookies.get(TOKEN_COOKIE_NAME)
    if not verify_token(token):
        return redirect(url_for("login"))
    return None


# -------------------------
# LOGIN PAGE
# -------------------------
login_form = """
<h2>Login</h2>
<form method="POST">
  Username: <input name="username"><br><br>
  Password: <input name="password" type="password"><br><br>
  <input type="submit" value="Login">
</form>
{% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            return render_template_string(login_form, error="Missing username or password.")

        try:
            r = requests.post(
                f"{AUTH_SERVICE_URL}/login",
                json={"username": username, "password": password},
                timeout=3
            )
        except requests.RequestException:
            return render_template_string(login_form, error="Auth service unreachable.")

        if r.status_code != 200:
            return render_template_string(login_form, error="Invalid credentials.")

        token = r.json().get("token")
        if not token:
            return render_template_string(login_form, error="Auth service returned no token.")

        resp = make_response(redirect(url_for("dashboard")))
        resp.set_cookie(TOKEN_COOKIE_NAME, token, httponly=True, samesite="Lax")
        return resp

    return render_template_string(login_form, error=None)


@app.route("/logout", methods=["POST", "GET"])
def logout():
    resp = make_response(redirect(url_for("login")))
    resp.set_cookie(TOKEN_COOKIE_NAME, "", expires=0)
    return resp


# -------------------------
# DASHBOARD (Central Hub)
# -------------------------
dashboard_page = '''
<h2>Dashboard</h2>
{% if success %}
  <p style="color:green; font-weight:bold;">{{ success }}</p>
{% endif %}
<p>What would you like to do?</p>
<ul>
  <li><a href="/customer">Add Customer</a></li>
  <li><a href="/product">Add Product</a></li>
  <li><a href="/sale">Record Sale</a></li>
</ul>
<br>
<a href="/logout">Logout</a>
'''

@app.route("/")
@app.route("/dashboard")
def dashboard():
    guard = require_auth()
    if guard:
        return guard

    success = request.args.get("success")
    return render_template_string(dashboard_page, success=success)


# -------------------------
# CUSTOMER FORM
# -------------------------
customer_form = '''
<h2>Add Customer</h2>
{% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
<form method="POST">
  Name: <input name="name" required><br><br>
  Email: <input name="email" type="email" required><br><br>
  <input type="submit" value="Submit">
</form>
<br>
<a href="/dashboard">Back to Dashboard</a>
'''

@app.route("/customer", methods=["GET", "POST"])
def index():
    guard = require_auth()
    if guard:
        return guard

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        # -- Proactive Validation --
        if not name:
            return render_template_string(customer_form, error="Customer name is required.")
        if not email:
            return render_template_string(customer_form, error="Email is required.")
        if "@" not in email or "." not in email:
            return render_template_string(customer_form, error="Please enter a valid email address.")

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Check for duplicate email
            cursor.execute("SELECT id FROM customers WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return render_template_string(customer_form, error="A customer with this email already exists.")

            cursor.execute(
                "INSERT INTO customers (name, email) VALUES (%s, %s)",
                (name, email)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for("dashboard", success="Customer added successfully!"))
        except Exception as e:
            return render_template_string(customer_form, error=f"Database error: {str(e)}")

    return render_template_string(customer_form, error=None)


# -------------------------
# PRODUCT FORM
# -------------------------
product_form = '''
<h2>Add Product</h2>
{% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
<form method="POST">
  Product Name: <input name="product_name" required><br><br>
  Price: <input name="price" type="number" step="0.01" min="0.01" required><br><br>
  <input type="submit" value="Submit">
</form>
<br>
<a href="/dashboard">Back to Dashboard</a>
'''

@app.route("/product", methods=["GET", "POST"])
def product():
    guard = require_auth()
    if guard:
        return guard

    if request.method == "POST":
        product_name = request.form.get("product_name", "").strip()
        price = request.form.get("price", "").strip()

        # -- Proactive Validation --
        if not product_name:
            return render_template_string(product_form, error="Product name is required.")
        if not price:
            return render_template_string(product_form, error="Price is required.")

        try:
            price = float(price)
        except ValueError:
            return render_template_string(product_form, error="Price must be a valid number.")

        if price <= 0:
            return render_template_string(product_form, error="Price must be greater than zero.")

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Check for duplicate product name
            cursor.execute("SELECT id FROM products WHERE name = %s", (product_name,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return render_template_string(product_form, error="A product with this name already exists.")

            cursor.execute(
                "INSERT INTO products (name, price) VALUES (%s, %s)",
                (product_name, price)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for("dashboard", success="Product added successfully!"))
        except Exception as e:
            return render_template_string(product_form, error=f"Database error: {str(e)}")

    return render_template_string(product_form, error=None)


# -------------------------
# SALE FORM
# -------------------------
sale_form = '''
<h2>Record Sale</h2>
{% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
<form method="POST">
  Customer ID: <input name="customer_id" type="number" min="1" required><br><br>
  Product ID: <input name="product_id" type="number" min="1" required><br><br>
  Quantity: <input name="quantity" type="number" min="1" required><br><br>
  <input type="submit" value="Submit">
</form>
<br>
<a href="/dashboard">Back to Dashboard</a>
'''

@app.route("/sale", methods=["GET", "POST"])
def sale():
    guard = require_auth()
    if guard:
        return guard

    if request.method == "POST":
        customer_id = request.form.get("customer_id", "").strip()
        product_id = request.form.get("product_id", "").strip()
        quantity = request.form.get("quantity", "").strip()

        # -- Proactive Validation --
        if not customer_id or not product_id or not quantity:
            return render_template_string(sale_form, error="All fields are required.")

        try:
            customer_id = int(customer_id)
            product_id = int(product_id)
            quantity = int(quantity)
        except ValueError:
            return render_template_string(sale_form, error="Customer ID, Product ID, and Quantity must be whole numbers.")

        if quantity <= 0:
            return render_template_string(sale_form, error="Quantity must be at least 1.")

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Check customer exists
            cursor.execute("SELECT id FROM customers WHERE id = %s", (customer_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return render_template_string(sale_form, error=f"Customer ID {customer_id} does not exist.")

            # Check product exists and fetch price
            cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()
            if not product:
                cursor.close()
                conn.close()
                return render_template_string(sale_form, error=f"Product ID {product_id} does not exist.")

            product_price = product[0]
            total_price = product_price * quantity
            order_date = date.today()

            cursor.execute(
                """INSERT INTO orders
                   (customer_id, product_id, quantity, total_price, order_date)
                   VALUES (%s, %s, %s, %s, %s)""",
                (customer_id, product_id, quantity, total_price, order_date)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for("dashboard", success=f"Sale recorded successfully! Total: ${total_price:.2f}"))
        except Exception as e:
            return render_template_string(sale_form, error=f"Database error: {str(e)}")

    return render_template_string(sale_form, error=None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)