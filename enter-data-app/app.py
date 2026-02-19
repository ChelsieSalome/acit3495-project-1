from flask import Flask, request, render_template_string, redirect, url_for, make_response
import mysql.connector
import requests
import os

app = Flask(__name__)

db_config = {
    "host": "mysql",
    "user": "user",
    "password": "password",
    "database": "project1"
}

# ---- Auth service config (service name inside docker-compose network) ----
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
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
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
            return render_template_string(login_form, error="Missing username or password")

        try:
            r = requests.post(
                f"{AUTH_SERVICE_URL}/login",
                json={"username": username, "password": password},
                timeout=3
            )
        except requests.RequestException:
            return render_template_string(login_form, error="Auth service unreachable")

        if r.status_code != 200:
            return render_template_string(login_form, error="Invalid credentials")

        token = r.json().get("token")
        if not token:
            return render_template_string(login_form, error="Auth service returned no token")

        resp = make_response(redirect(url_for("index")))
        # HttpOnly cookie so JS can’t read it
        resp.set_cookie(TOKEN_COOKIE_NAME, token, httponly=True, samesite="Lax")
        return resp

    return render_template_string(login_form, error=None)

@app.route("/logout", methods=["POST", "GET"])
def logout():
    resp = make_response(redirect(url_for("login")))
    resp.set_cookie(TOKEN_COOKIE_NAME, "", expires=0)
    return resp


# -------------------------
# CUSTOMER FORM (existing)
# -------------------------
customer_form = '''
<h2>Add Customer</h2>
<form method="POST">
  Name: <input name="name"><br>
  Email: <input name="email"><br>
  <input type="submit" value="Submit">
</form>

<p>
  <a href="/product">Add Product</a> |
  <a href="/sale">Record Sale</a> |
  <a href="/login">Login</a> |
  <a href="/logout">Logout</a>
</p>
'''

@app.route("/", methods=["GET", "POST"])
def index():
    guard = require_auth()
    if guard:
        return guard

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
<h2>Add Product</h2>
<form method="POST">
  Product Name: <input name="product_name"><br>
  Price: <input name="price" type="number" step="0.01"><br>
  <input type="submit" value="Submit">
</form>

<p>
  <a href="/">Add Customer</a> |
  <a href="/sale">Record Sale</a> |
  <a href="/logout">Logout</a>
</p>
'''

@app.route("/product", methods=["GET", "POST"])
def product():
    guard = require_auth()
    if guard:
        return guard

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
<h2>Record Sale</h2>
<form method="POST">
  Customer ID: <input name="customer_id" type="number"><br>
  Product ID: <input name="product_id" type="number"><br>
  Quantity: <input name="quantity" type="number"><br>
  <input type="submit" value="Submit">
</form>

<p>
  <a href="/">Add Customer</a> |
  <a href="/product">Add Product</a> |
  <a href="/logout">Logout</a>
</p>
'''

@app.route("/sale", methods=["GET", "POST"])
def sale():
    guard = require_auth()
    if guard:
        return guard

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