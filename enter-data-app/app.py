from flask import Flask, request, render_template_string, redirect, url_for, make_response, jsonify
import mysql.connector
import requests
import os
import logging
from datetime import date, datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_config = {
    "host":     os.environ.get("MYSQL_HOST",     "mysql"),
    "user":     os.environ.get("MYSQL_USER",     "user"),
    "password": os.environ.get("MYSQL_PASSWORD", "password"),
    "database": os.environ.get("MYSQL_DATABASE", "project1")
}

AUTH_SERVICE_URL  = os.environ.get("AUTH_SERVICE_URL", "http://auth-service:5001")
TOKEN_COOKIE_NAME = "auth_token"



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



SHARED_CSS = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: Arial, sans-serif;
        background: #f0f2f5;
        min-height: 100vh;
    }
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: white;
        padding: 16px 28px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 28px;
    }
    .header h1 { font-size: 1.4rem; color: #333; }
    .header-links a {
        margin-left: 16px;
        text-decoration: none;
        font-size: 0.9rem;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: bold;
    }
    .btn-primary   { background: #4A90D9; color: white; }
    .btn-primary:hover { background: #357ABD; }
    .btn-logout    { background: #e74c3c; color: white; }
    .btn-logout:hover  { background: #c0392b; }
    .btn-secondary { background: #f0f2f5; color: #333; border: 1px solid #ddd; }
    .btn-secondary:hover { background: #e2e5e9; }

    .page-body {
        padding: 30px 20px;
    }

    /* Card */
    .card {
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        padding: 32px;
        max-width: 480px;
        margin: 0 auto;
    }
    .card-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #888;
        margin-bottom: 4px;
        font-weight: bold;
    }
    .card-name {
        font-size: 1.4rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 24px;
    }

    /* Form Elements */
    label {
        display: block;
        margin-bottom: 4px;
        font-size: 0.875rem;
        color: #555;
        font-weight: bold;
    }
    input[type=text],
    input[type=email],
    input[type=password],
    input[type=number] {
        width: 100%;
        padding: 10px 12px;
        margin-bottom: 18px;
        border: 1px solid #ccc;
        border-radius: 6px;
        font-size: 0.95rem;
    }
    input[type=text]:focus,
    input[type=email]:focus,
    input[type=password]:focus,
    input[type=number]:focus {
        outline: none;
        border-color: #4A90D9;
        box-shadow: 0 0 0 2px rgba(74,144,217,0.15);
    }
    input[type=submit] {
        width: 100%;
        padding: 11px;
        background: #4A90D9;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 1rem;
        cursor: pointer;
        font-weight: bold;
        margin-top: 4px;
    }
    input[type=submit]:hover { background: #357ABD; }

    /* Alerts */
    .alert-error {
        background: #ffe0e0;
        color: #c0392b;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 18px;
        font-size: 0.875rem;
    }
    .alert-success {
        background: #eafaf1;
        color: #27ae60;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 18px;
        font-size: 0.875rem;
        font-weight: bold;
    }

    /* Dashboard nav cards */
    .nav-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 20px;
        max-width: 700px;
        margin: 0 auto;
    }
    @media (max-width: 640px) {
        .nav-grid { grid-template-columns: 1fr; }
    }
    .nav-card {
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        padding: 28px 20px;
        text-align: center;
        text-decoration: none;
        color: #2c3e50;
        font-weight: bold;
        font-size: 1rem;
        transition: box-shadow 0.2s, transform 0.2s;
        display: block;
    }
    .nav-card:hover {
        box-shadow: 0 4px 18px rgba(0,0,0,0.13);
        transform: translateY(-2px);
    }
    .nav-card .nav-icon {
        font-size: 2rem;
        margin-bottom: 10px;
        display: block;
    }
    .nav-card-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #888;
        margin-bottom: 6px;
        font-weight: bold;
    }

    /* Back link */
    .back-link {
        display: inline-block;
        margin-top: 18px;
        color: #4A90D9;
        text-decoration: none;
        font-size: 0.9rem;
    }
    .back-link:hover { text-decoration: underline; }
"""



LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Enter Data - Login</title>
    <style>
        """ + SHARED_CSS + """
        body {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-wrap {
            width: 100%;
            max-width: 380px;
            padding: 20px;
        }
        .card h2 {
            text-align: center;
            margin-bottom: 24px;
            color: #333;
            font-size: 1.5rem;
        }
    </style>
</head>
<body>
    <div class="login-wrap">
        <div class="card">
            <h2>Enter Data Portal</h2>
            {% if error %}
                <div class="alert-error">{{ error }}</div>
            {% endif %}
            <form method="POST">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" placeholder="Enter username" required>
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter password" required>
                <input type="submit" value="Login">
            </form>
        </div>
    </div>
</body>
</html>
"""


DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <style>""" + SHARED_CSS + """</style>
</head>
<body>
    <div class="page-body">

        <div class="header">
            <h1>What would you like to do?</h1>
            <div class="header-links">
                <a href="/logout" class="btn-logout">Logout</a>
            </div>
        </div>

        {% if success %}
            <div style="max-width:700px; margin: 0 auto 24px auto;">
                <div class="alert-success">{{ success }}</div>
            </div>
        {% endif %}

        <div class="nav-grid">
            <a href="/customer" class="nav-card">
                Add Customer
            </a>
            <a href="/product" class="nav-card">
                Add Product
            </a>
            <a href="/sale" class="nav-card">
                Record Sale
            </a>
        </div>

    </div>
</body>
</html>
"""


CUSTOMER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Add Customer</title>
    <style>""" + SHARED_CSS + """</style>
</head>
<body>
    <div class="page-body">

        <div class="header">
            <h1>Welcome !!</h1>
            <div class="header-links">
                <a href="/dashboard" class="btn-secondary">Dashboard</a>
                <a href="/logout" class="btn-logout">Logout</a>
            </div>
        </div>

        <div class="card">
            <div class="card-title">Manage</div>
            <div class="card-name">Add Customer</div>

            {% if error %}
                <div class="alert-error">{{ error }}</div>
            {% endif %}

            <form method="POST">
                <label for="name">Full Name</label>
                <input type="text" id="name" name="name" placeholder="Enter customer name" required>

                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" placeholder="Enter email address" required>

                <input type="submit" value="Add Customer">
            </form>

            <a href="/dashboard" class="back-link">Back to Dashboard</a>
        </div>

    </div>
</body>
</html>
"""


PRODUCT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Add Product</title>
    <style>""" + SHARED_CSS + """</style>
</head>
<body>
    <div class="page-body">

        <div class="header">
            <h1>Enter Data Portal</h1>
            <div class="header-links">
                <a href="/dashboard" class="btn-secondary">Dashboard</a>
                <a href="/logout" class="btn-logout">Logout</a>
            </div>
        </div>

        <div class="card">
            <div class="card-title">Manage</div>
            <div class="card-name">Add Product</div>

            {% if error %}
                <div class="alert-error">{{ error }}</div>
            {% endif %}

            <form method="POST">
                <label for="product_name">Product Name</label>
                <input type="text" id="product_name" name="product_name" placeholder="Enter product name" required>

                <label for="price">Price ($)</label>
                <input type="number" id="price" name="price" step="0.01" min="0.01" placeholder="0.00" required>

                <input type="submit" value="Add Product">
            </form>

            <a href="/dashboard" class="back-link">Back to Dashboard</a>
        </div>

    </div>
</body>
</html>
"""


SALE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Record Sale</title>
    <style>""" + SHARED_CSS + """</style>
</head>
<body>
    <div class="page-body">

        <div class="header">
            <h1>Enter Data Portal</h1>
            <div class="header-links">
                <a href="/dashboard" class="btn-secondary">Dashboard</a>
                <a href="/logout" class="btn-logout">Logout</a>
            </div>
        </div>

        <div class="card">
            <div class="card-title">Manage</div>
            <div class="card-name">Record Sale</div>

            {% if error %}
                <div class="alert-error">{{ error }}</div>
            {% endif %}

            <form method="POST">
                <label for="customer_id">Customer ID</label>
                <input type="number" id="customer_id" name="customer_id" min="1" placeholder="Enter customer ID" required>

                <label for="product_id">Product ID</label>
                <input type="number" id="product_id" name="product_id" min="1" placeholder="Enter product ID" required>

                <label for="quantity">Quantity</label>
                <input type="number" id="quantity" name="quantity" min="1" placeholder="Enter quantity" required>

                <input type="submit" value="Record Sale">
            </form>

            <a href="/dashboard" class="back-link">Back to Dashboard</a>
        </div>

    </div>
</body>
</html>
"""



@app.route("/")
@app.route("/dashboard")
def dashboard():
    guard = require_auth()
    if guard:
        return guard
    success = request.args.get("success")
    return render_template_string(DASHBOARD_TEMPLATE, success=success)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            return render_template_string(LOGIN_TEMPLATE, error="Username and password are required.")

        try:
            r = requests.post(
                f"{AUTH_SERVICE_URL}/login",
                json={"username": username, "password": password},
                timeout=3
            )
        except requests.RequestException:
            return render_template_string(LOGIN_TEMPLATE, error="Auth service is unreachable. Please try again.")

        if r.status_code != 200:
            return render_template_string(LOGIN_TEMPLATE, error="Invalid username or password.")

        token = r.json().get("token")
        if not token:
            return render_template_string(LOGIN_TEMPLATE, error="Auth service returned no token.")

        resp = make_response(redirect(url_for("dashboard")))
        resp.set_cookie(TOKEN_COOKIE_NAME, token, httponly=True, samesite="Lax")
        return resp

    return render_template_string(LOGIN_TEMPLATE, error=None)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    resp = make_response(redirect(url_for("login")))
    resp.set_cookie(TOKEN_COOKIE_NAME, "", expires=0)
    return resp


@app.route("/customer", methods=["GET", "POST"])
def index():
    guard = require_auth()
    if guard:
        return guard

    if request.method == "POST":
        name  = request.form.get("name",  "").strip()
        email = request.form.get("email", "").strip()

        if not name:
            return render_template_string(CUSTOMER_TEMPLATE, error="Customer name is required.")
        if not email:
            return render_template_string(CUSTOMER_TEMPLATE, error="Email is required.")
        if "@" not in email or "." not in email:
            return render_template_string(CUSTOMER_TEMPLATE, error="Please enter a valid email address.")

        try:
            conn   = mysql.connector.connect(**db_config)
            cursor = conn.cursor(buffered=True)

            cursor.execute("SELECT customer_id FROM customers WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close(); conn.close()
                return render_template_string(CUSTOMER_TEMPLATE, error="A customer with this email already exists.")

            cursor.execute(
                "INSERT INTO customers (customer_name, email) VALUES (%s, %s)",
                (name, email)
            )
            conn.commit()
            cursor.close(); conn.close()
            return redirect(url_for("dashboard", success="Customer added successfully!"))
        except Exception as e:
            return render_template_string(CUSTOMER_TEMPLATE, error=f"Database error: {str(e)}")

    return render_template_string(CUSTOMER_TEMPLATE, error=None)


@app.route("/product", methods=["GET", "POST"])
def product():
    guard = require_auth()
    if guard:
        return guard

    if request.method == "POST":
        product_name = request.form.get("product_name", "").strip()
        price        = request.form.get("price", "").strip()

        if not product_name:
            return render_template_string(PRODUCT_TEMPLATE, error="Product name is required.")
        if not price:
            return render_template_string(PRODUCT_TEMPLATE, error="Price is required.")

        try:
            price = float(price)
        except ValueError:
            return render_template_string(PRODUCT_TEMPLATE, error="Price must be a valid number.")

        if price <= 0:
            return render_template_string(PRODUCT_TEMPLATE, error="Price must be greater than zero.")

        try:
            conn   = mysql.connector.connect(**db_config)
            cursor = conn.cursor(buffered=True)

            cursor.execute("SELECT product_id FROM products WHERE product_name = %s", (product_name,))
            if cursor.fetchone():
                cursor.close(); conn.close()
                return render_template_string(PRODUCT_TEMPLATE, error="A product with this name already exists.")

            cursor.execute(
                "INSERT INTO products (product_name, product_price) VALUES (%s, %s)",
                (product_name, price)
            )
            conn.commit()
            cursor.close(); conn.close()
            return redirect(url_for("dashboard", success="Product added successfully!"))
        except Exception as e:
            return render_template_string(PRODUCT_TEMPLATE, error=f"Database error: {str(e)}")

    return render_template_string(PRODUCT_TEMPLATE, error=None)


@app.route("/sale", methods=["GET", "POST"])
def sale():
    guard = require_auth()
    if guard:
        return guard

    if request.method == "POST":
        customer_id = request.form.get("customer_id", "").strip()
        product_id  = request.form.get("product_id",  "").strip()
        quantity    = request.form.get("quantity",    "").strip()

        if not customer_id or not product_id or not quantity:
            return render_template_string(SALE_TEMPLATE, error="All fields are required.")

        try:
            customer_id = int(customer_id)
            product_id  = int(product_id)
            quantity    = int(quantity)
        except ValueError:
            return render_template_string(SALE_TEMPLATE, error="Customer ID, Product ID, and Quantity must be whole numbers.")

        if quantity <= 0:
            return render_template_string(SALE_TEMPLATE, error="Quantity must be at least 1.")

        try:
            conn   = mysql.connector.connect(**db_config)
            cursor = conn.cursor(buffered=True)

            cursor.execute("SELECT customer_id FROM customers WHERE customer_id = %s", (customer_id,))
            if not cursor.fetchone():
                cursor.close(); conn.close()
                return render_template_string(SALE_TEMPLATE, error=f"Customer ID {customer_id} does not exist.")

            cursor.execute("SELECT product_price FROM products WHERE product_id = %s", (product_id,))
            prod = cursor.fetchone()
            if not prod:
                cursor.close(); conn.close()
                return render_template_string(SALE_TEMPLATE, error=f"Product ID {product_id} does not exist.")

            product_price  = prod[0]
            total_price    = product_price * quantity
            purchase_date  = date.today()

            cursor.execute(
                """INSERT INTO orders (customer_id, product_id, quantity, purchase_date)
                   VALUES (%s, %s, %s, %s)""",
                (customer_id, product_id, quantity, purchase_date)
            )
            conn.commit()
            cursor.close(); conn.close()
            return redirect(url_for("dashboard", success=f"Sale recorded successfully! Total: ${total_price:.2f}"))
        except Exception as e:
            return render_template_string(SALE_TEMPLATE, error=f"Database error: {str(e)}")

    return render_template_string(SALE_TEMPLATE, error=None)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":    "ok",
        "service":   "enter-data-app",
        "timestamp": datetime.utcnow().isoformat()
    }), 200



if __name__ == "__main__":
    port  = int(os.environ.get("ENTER_DATA_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    logger.info(f"Starting Enter Data App on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
