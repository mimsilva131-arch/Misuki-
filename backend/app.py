
import os
import secrets
from urllib.parse import urlencode

import requests

from flask import (
    Flask,
    render_template,
    send_from_directory,
    redirect,
    request,
    session,
)

from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

WEBSITE_DIR = os.path.join(
    BASE_DIR,
    "website"
)

CSS_DIR = os.path.join(
    BASE_DIR,
    "css"
)

JS_DIR = os.path.join(
    BASE_DIR,
    "js"
)

ASSETS_DIR = os.path.join(
    BASE_DIR,
    "assets"
)


# =========================================================
# DISCORD OAUTH2
# =========================================================

DISCORD_CLIENT_ID = os.getenv(
    "DISCORD_CLIENT_ID"
)

DISCORD_CLIENT_SECRET = os.getenv(
    "DISCORD_CLIENT_SECRET"
)

DISCORD_LOGIN_REDIRECT_URI = os.getenv(
    "DISCORD_LOGIN_REDIRECT_URI"
)

DISCORD_API = (
    "https://discord.com/api/v10"
)

DISCORD_OAUTH_URL = (
    "https://discord.com/oauth2/authorize"
)

DISCORD_TOKEN_URL = (
    f"{DISCORD_API}/oauth2/token"
)


# =========================================================
# FLASK
# =========================================================

app = Flask(
    __name__,
    template_folder=WEBSITE_DIR,
    static_folder=None
)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    os.getenv(
        "SECRET_KEY",
        "misuki-development-key"
    )
)

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1
)


# =========================================================
# SESSION
# =========================================================

app.config["SESSION_COOKIE_HTTPONLY"] = True

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config["SESSION_COOKIE_SECURE"] = (
    os.getenv(
        "COOKIE_SECURE",
        "false"
    ).lower() == "true"
)

app.config["PERMANENT_SESSION_LIFETIME"] = 86400


# =========================================================
# HELPERS
# =========================================================

def error_page(
    title,
    message,
    status_code=400
):
    return render_template(
        "error.html",
        title=title,
        message=message
    ), status_code


def create_oauth_state():
    state = secrets.token_urlsafe(32)

    session["oauth_state"] = state

    return state


def verify_oauth_state(state):

    stored_state = session.pop(
        "oauth_state",
        None
    )

    if not state:
        return False

    if not stored_state:
        return False

    return secrets.compare_digest(
        str(stored_state),
        str(state)
    )


def get_user():

    access_token = session.get(
        "access_token"
    )

    if not access_token:
        return None

    try:

        response = requests.get(
            f"{DISCORD_API}/users/@me",
            headers={
                "Authorization":
                    f"Bearer {access_token}"
            },
            timeout=10
        )

    except requests.RequestException as error:

        print(
            f"❌ Discord user request error: {error}"
        )

        return None

    if response.status_code != 200:

        if response.status_code in (
            401,
            403
        ):
            session.clear()

        return None

    try:
        return response.json()

    except ValueError:
        return None


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    user = get_user()

    return render_template(
        "index.html",
        user=user
    )


# =========================================================
# DISCORD LOGIN
# =========================================================

@app.route("/login")
def login():

    if not DISCORD_CLIENT_ID:

        return error_page(
            "Configuration Error",
            "DISCORD_CLIENT_ID is missing.",
            500
        )

    if not DISCORD_CLIENT_SECRET:

        return error_page(
            "Configuration Error",
            "DISCORD_CLIENT_SECRET is missing.",
            500
        )

    if not DISCORD_LOGIN_REDIRECT_URI:

        return error_page(
            "Configuration Error",
            "DISCORD_LOGIN_REDIRECT_URI is missing.",
            500
        )

    next_url = request.args.get(
        "next",
        "/dashboard"
    )

    if (
        not next_url.startswith("/")
        or next_url.startswith("//")
    ):
        next_url = "/dashboard"

    session["next_url"] = next_url

    state = create_oauth_state()

    params = {
        "client_id":
            DISCORD_CLIENT_ID,

        "response_type":
            "code",

        "redirect_uri":
            DISCORD_LOGIN_REDIRECT_URI,

        "scope":
            "identify guilds",

        "state":
            state
    }

    discord_url = (
        f"{DISCORD_OAUTH_URL}?"
        + urlencode(params)
    )

    print(
        "🔐 Starting Discord OAuth2 login"
    )

    print(
        f"🔗 Redirect URI: "
        f"{DISCORD_LOGIN_REDIRECT_URI}"
    )

    return redirect(
        discord_url
    )


# =========================================================
# DISCORD LOGIN CALLBACK
# =========================================================

@app.route("/login/callback")
def login_callback():

    error = request.args.get(
        "error"
    )

    if error:

        session.pop(
            "oauth_state",
            None
        )

        return error_page(
            "OAuth2 Error",
            "Discord cancelled or rejected the login.",
            400
        )

    state = request.args.get(
        "state"
    )

    if not verify_oauth_state(
        state
    ):

        return error_page(
            "OAuth2 Error",
            "Invalid or expired OAuth2 state.",
            400
        )

    code = request.args.get(
        "code"
    )

    if not code:

        return error_page(
            "OAuth2 Error",
            "No authorization code was received.",
            400
        )

    if not DISCORD_CLIENT_ID:

        return error_page(
            "Configuration Error",
            "DISCORD_CLIENT_ID is missing.",
            500
        )

    if not DISCORD_CLIENT_SECRET:

        return error_page(
            "Configuration Error",
            "DISCORD_CLIENT_SECRET is missing.",
            500
        )

    if not DISCORD_LOGIN_REDIRECT_URI:

        return error_page(
            "Configuration Error",
            "DISCORD_LOGIN_REDIRECT_URI is missing.",
            500
        )

    # -----------------------------------------------------
    # EXCHANGE CODE FOR TOKEN
    # -----------------------------------------------------

    token_data = {

        "client_id":
            DISCORD_CLIENT_ID,

        "client_secret":
            DISCORD_CLIENT_SECRET,

        "grant_type":
            "authorization_code",

        "code":
            code,

        "redirect_uri":
            DISCORD_LOGIN_REDIRECT_URI
    }

    try:

        response = requests.post(

            DISCORD_TOKEN_URL,

            data=token_data,

            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded"
            },

            timeout=10
        )

    except requests.RequestException as error:

        print(
            f"❌ Discord token request error: {error}"
        )

        return error_page(
            "OAuth2 Error",
            "Could not contact Discord.",
            500
        )

    if response.status_code != 200:

        print(
            "❌ Discord token exchange failed:"
        )

        print(
            response.text
        )

        return error_page(
            "OAuth2 Error",
            "Discord rejected the authorization code.",
            400
        )

    try:

        token_json = response.json()

    except ValueError:

        return error_page(
            "OAuth2 Error",
            "Discord returned an invalid token response.",
            400
        )

    access_token = token_json.get(
        "access_token"
    )

    if not access_token:

        return error_page(
            "OAuth2 Error",
            "Discord did not return an access token.",
            400
        )

    # -----------------------------------------------------
    # GET DISCORD USER
    # -----------------------------------------------------

    try:

        user_response = requests.get(

            f"{DISCORD_API}/users/@me",

            headers={
                "Authorization":
                    f"Bearer {access_token}"
            },

            timeout=10
        )

    except requests.RequestException as error:

        print(
            f"❌ Discord user request error: {error}"
        )

        return error_page(
            "OAuth2 Error",
            "Could not retrieve your Discord account.",
            500
        )

    if user_response.status_code != 200:

        return error_page(
            "OAuth2 Error",
            "Could not verify your Discord account.",
            400
        )

    try:

        user = user_response.json()

    except ValueError:

        return error_page(
            "OAuth2 Error",
            "Discord returned invalid user information.",
            400
        )

    # -----------------------------------------------------
    # SAVE SESSION
    # -----------------------------------------------------

    next_url = session.get(
        "next_url",
        "/dashboard"
    )

    if (
        not next_url.startswith("/")
        or next_url.startswith("//")
    ):
        next_url = "/dashboard"

    session.clear()

    session["access_token"] = (
        access_token
    )

    session["logged_in"] = True

    session["user_id"] = user.get(
        "id"
    )

    session["username"] = (
        user.get("global_name")
        or user.get("username")
        or "Discord User"
    )

    session.permanent = True

    print(
        "=========================================="
    )

    print(
        "✅ DISCORD LOGIN SUCCESSFUL"
    )

    print(
        f"👤 User: "
        f"{user.get('username')}"
    )

    print(
        f"🆔 ID: "
        f"{user.get('id')}"
    )

    print(
        f"➡️ Next: "
        f"{next_url}"
    )

    print(
        "=========================================="
    )

    return redirect(
        next_url
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        "/"
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    user = get_user()

    if not user:

        session["next_url"] = (
            "/dashboard"
        )

        return redirect(
            "/login"
        )

    return render_template(
        "dashboard.html",
        user=user
    )


# =========================================================
# WEBSITE PAGES
# =========================================================

@app.route("/<page>")
def website_page(page):

    allowed_pages = {

        "manage",
        "reviews",
        "documentation",
        "support",
        "terms",
        "privacy",
        "data",
        "cookies",

    }

    if page not in allowed_pages:

        return "Page not found", 404

    user = get_user()

    return render_template(
        f"{page}.html",
        user=user
    )


# =========================================================
# CSS
# =========================================================

@app.route("/css/<path:filename>")
def css(filename):

    return send_from_directory(
        CSS_DIR,
        filename
    )


# =========================================================
# JAVASCRIPT
# =========================================================

@app.route("/js/<path:filename>")
def javascript(filename):

    return send_from_directory(
        JS_DIR,
        filename
    )


# =========================================================
# ASSETS
# =========================================================

@app.route("/assets/<path:filename>")
def assets(filename):

    return send_from_directory(
        ASSETS_DIR,
        filename
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    print(
        "=========================================="
    )

    print(
        "🌐 Misuki Web Server"
    )

    print(
        "=========================================="
    )

    print(
        f"🔐 Client ID configured: "
        f"{bool(DISCORD_CLIENT_ID)}"
    )

    print(
        f"🔑 Client Secret configured: "
        f"{bool(DISCORD_CLIENT_SECRET)}"
    )

    print(
        f"🔗 Login Redirect: "
        f"{DISCORD_LOGIN_REDIRECT_URI}"
    )

    print(
        "=========================================="
    )

    app.run(
        host="0.0.0.0",
        port=int(
            os.getenv(
                "PORT",
                5000
            )
        ),
        debug=False
    )

