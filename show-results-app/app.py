import os
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for, make_response
import requests
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# Auth config
# -------------------------
AUTH_SERVICE_URL  = os.environ.get("AUTH_SERVICE_URL", "http://auth-service:5001")
TOKEN_COOKIE_NAME = "auth_token"

# -------------------------
# Mongo config
# -------------------------
MONGO_URI        = os.environ.get("MONGO_URI",        "mongodb://mongodb:27017")
MONGO_DB         = os.environ.get("MONGO_DB",         "analytics_db")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "analytics")

# Create Mongo client
mongo_client = MongoClient(MONGO_URI)

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
# Shared CSS
# -------------------------
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
    .btn-primary        { background: #4A90D9; color: white; }
    .btn-primary:hover  { background: #357ABD; }
    .btn-logout         { background: #e74c3c; color: white; }
    .btn-logout:hover   { background: #c0392b; }
    .btn-secondary      { background: #f0f2f5; color: #333; border: 1px solid #ddd; }
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
        max-width: 560px;
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

    /* Form Elements */
    label {
        display: block;
        margin-bottom: 4px;
        font-size: 0.875rem;
        color: #555;
        font-weight: bold;
    }
    input[type=text],
    input[type=password] {
        width: 100%;
        padding: 10px 12px;
        margin-bottom: 18px;
        border: 1px solid #ccc;
        border-radius: 6px;
        font-size: 0.95rem;
    }
    input[type=text]:focus,
    input[type=password]:focus {
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

    /* Analytics Table */
    .analytics-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 8px;
    }
    .analytics-table th {
        text-align: left;
        padding: 10px 14px;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #888;
        border-bottom: 2px solid #f0f2f5;
        font-weight: bold;
    }
    .analytics-table td {
        padding: 12px 14px;
        font-size: 0.95rem;
        color: #2c3e50;
        border-bottom: 1px solid #f0f2f5;
    }
    .analytics-table tr:last-child td {
        border-bottom: none;
    }
    .analytics-table td:first-child {
        color: #555;
        font-weight: bold;
        width: 55%;
    }

    /* Last updated */
    .last-updated {
        font-size: 0.8rem;
        color: #aaa;
        margin-bottom: 20px;
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


# -------------------------
# Templates
# -------------------------
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Show Results - Login</title>
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
            <h2>Show Results</h2>
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

RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Analytics Results</title>
    <style>""" + SHARED_CSS + """</style>
</head>
<body>
    <div class="page-body">

        <div class="header">
            <h1>Analytics Results</h1>
            <div class="header-links">
                <a href="/results" class="btn-secondary">Refresh</a>
                <a href="/logout" class="btn-logout">Logout</a>
            </div>
        </div>

        <div class="card">
            <div class="card-title">Overview</div>
            <div class="card-name">Latest Analytics</div>

            {% if updated_at %}
                <p class="last-updated">Last Updated: {{ updated_at }}</p>
            {% else %}
                <p class="last-updated">Last Updated: Unknown</p>
            {% endif %}

            {% if error %}
                <div class="alert-error">{{ error }}</div>
            {% endif %}

            <table class="analytics-table">
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                {% for item in items %}
                <tr>
                    <td>{{ item.label }}</td>
                    <td>{{ item.value }}</td>
                </tr>
                {% endfor %}
            </table>

        </div>

    </div>
</body>
</html>
"""


# -------------------------
# Mongo fetch layer
# -------------------------
def fetch_analytics_from_mongo() -> dict:
    try:
        db  = mongo_client[MONGO_DB]
        col = db[MONGO_COLLECTION]

        doc = col.find_one({"type": "latest"}, {"_id": 0})

        if not doc:
            return {
                "updated_at": None,
                "items": [
                    {"label": "Status", "value": "No analytics document found yet"},
                ],
            }

        timestamp = doc.get("timestamp")
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()

        hsp = doc.get("highest_selling_product", {})
        tc  = doc.get("top_customer", {})

        items = [
            {"label": "Top Product",         "value": hsp.get("product_name",        "N/A")},
            {"label": "Total Quantity Sold",  "value": hsp.get("total_quantity_sold",  "N/A")},
            {"label": "Top Customer",         "value": tc.get("customer_name",         "N/A")},
            {"label": "Total Purchase Value", "value": f"${tc.get('total_purchase_value', 0):.2f}"},
        ]

        return {
            "updated_at": timestamp,
            "items":      items,
        }

    except PyMongoError as e:
        return {
            "updated_at": None,
            "items": [
                {"label": "Mongo Error", "value": str(e)},
            ],
        }


# -------------------------
# Routes
# -------------------------
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

        resp = make_response(redirect(url_for("results")))
        resp.set_cookie(TOKEN_COOKIE_NAME, token, httponly=True, samesite="Lax")
        return resp

    return render_template_string(LOGIN_TEMPLATE, error=None)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    resp = make_response(redirect(url_for("login")))
    resp.set_cookie(TOKEN_COOKIE_NAME, "", expires=0)
    return resp


@app.route("/")
def home():
    return redirect(url_for("results"))


@app.route("/results")
def results():
    guard = require_auth()
    if guard:
        return guard

    data = fetch_analytics_from_mongo()
    return render_template_string(
        RESULTS_TEMPLATE,
        updated_at=data.get("updated_at"),
        items=data.get("items", []),
    )


@app.route("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    logger.info("Starting Show Results App on port 5002")
    app.run(host="0.0.0.0", port=5002)
