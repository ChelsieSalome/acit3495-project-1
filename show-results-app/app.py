import os
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for, make_response
import requests
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)

# -------------------------
# Auth config
# -------------------------
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth-service:5001")
TOKEN_COOKIE_NAME = "auth_token"

# -------------------------
# Mongo config (placeholders)
# -------------------------
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongodb:27017")
MONGO_DB = os.environ.get("MONGO_DB", "project1")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "analytics_results")

# Create Mongo client (lazy safe usage in fetch function)
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
# Login / Logout
# -------------------------
login_form = """
<h2>Show Results - Login</h2>
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

        resp = make_response(redirect(url_for("results")))
        resp.set_cookie(TOKEN_COOKIE_NAME, token, httponly=True, samesite="Lax")
        return resp

    return render_template_string(login_form, error=None)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    resp = make_response(redirect(url_for("login")))
    resp.set_cookie(TOKEN_COOKIE_NAME, "", expires=0)
    return resp

# -------------------------
# Mongo fetch layer (EDIT THIS LATER)
# -------------------------
def fetch_analytics_from_mongo() -> dict:
    """
    Placeholder function.
    Once you know the Mongo schema, edit ONLY this function.

    Return format used by the UI:
    {
      "updated_at": "...",
      "items": [
        {"label": "Total Sales", "value": 123},
        {"label": "Max Quantity", "value": 10},
        {"label": "Min Quantity", "value": 1},
        {"label": "Average Quantity", "value": 4.2},
      ]
    }
    """
    try:
        db = mongo_client[MONGO_DB]
        col = db[MONGO_COLLECTION]

        # --- Placeholder query: get most recent analytics doc (common pattern) ---
        doc = col.find_one(sort=[("updated_at", -1)])

        if not doc:
            return {
                "updated_at": None,
                "items": [
                    {"label": "Status", "value": "No analytics document found yet"},
                ],
            }

        # --- Schema-agnostic: show keys for now ---
        # Remove Mongo _id from display
        doc.pop("_id", None)

        items = []
        for k, v in doc.items():
            items.append({"label": str(k), "value": str(v)})

        return {
            "updated_at": doc.get("updated_at"),
            "items": items,
        }

    except PyMongoError as e:
        return {
            "updated_at": None,
            "items": [
                {"label": "Mongo Error", "value": str(e)},
            ],
        }

# -------------------------
# Results UI (protected)
# -------------------------
results_page = """
<h2>Analytics Results</h2>

<p>
  <a href="/results">Refresh</a> |
  <a href="/logout">Logout</a>
</p>

{% if updated_at %}
<p><b>Last Updated:</b> {{ updated_at }}</p>
{% else %}
<p><b>Last Updated:</b> (unknown)</p>
{% endif %}

<table border="1" cellpadding="6" cellspacing="0">
  <tr><th>Metric</th><th>Value</th></tr>
  {% for item in items %}
    <tr>
      <td>{{ item.label }}</td>
      <td>{{ item.value }}</td>
    </tr>
  {% endfor %}
</table>
"""

@app.route("/")
def home():
    # Just redirect to results; auth will handle login redirect if needed
    return redirect(url_for("results"))

@app.route("/results")
def results():
    guard = require_auth()
    if guard:
        return guard

    data = fetch_analytics_from_mongo()
    return render_template_string(
        results_page,
        updated_at=data.get("updated_at"),
        items=data.get("items", []),
    )

@app.route("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
