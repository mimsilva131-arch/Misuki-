
import os
import random
import secrets

from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import requests
import psycopg2
import psycopg2.extras

from flask import (
    Flask,
    redirect,
    session,
    request,
    render_template,
    send_from_directory
)

from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# CONFIGURATION
# =========================================================

CLIENT_ID = os.getenv(
    "DISCORD_CLIENT_ID"
)

CLIENT_SECRET = os.getenv(
    "DISCORD_CLIENT_SECRET"
)


# =========================================================
# DISCORD LOGIN REDIRECT
# =========================================================

DISCORD_LOGIN_REDIRECT_URI = os.getenv(
    "DISCORD_LOGIN_REDIRECT_URI"
)


# =========================================================
# BOT TOKEN
# =========================================================

BOT_TOKEN = (
    os.getenv("DISCORD_BOT_TOKEN")
    or os.getenv("DISCORD_TOKEN")
)


# =========================================================
# DATABASE
# =========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)


# =========================================================
# FLASK SECRET
# =========================================================

SECRET_KEY = os.getenv(
    "FLASK_SECRET_KEY"
)


# =========================================================
# PORT
# =========================================================

PORT = int(
    os.getenv(
        "PORT",
        "5000"
    )
)


# =========================================================
# COOKIE CONFIGURATION
# =========================================================

SESSION_SECURE = True

SESSION_SAMESITE = "Lax"


print(
    "🍪 Cookie Config: "
    f"Secure={SESSION_SECURE}, "
    f"SameSite={SESSION_SAMESITE}"
)


# =========================================================
# SECRET KEY
# =========================================================

if not SECRET_KEY:

    SECRET_KEY = secrets.token_hex(32)

    print(
        "⚠️ FLASK_SECRET_KEY is missing."
    )

    print(
        "⚠️ A temporary Flask secret was generated."
    )

    print(
        "⚠️ Set FLASK_SECRET_KEY permanently in Render."
    )


# =========================================================
# DATABASE CHECK
# =========================================================

if not DATABASE_URL:

    print(
        "❌ DATABASE_URL is missing."
    )

    print(
        "❌ PostgreSQL is required for Misuki."
    )


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
# FLASK
# =========================================================

app = Flask(
    __name__,
    template_folder=WEBSITE_DIR,
    static_folder=None
)


app.secret_key = SECRET_KEY


# =========================================================
# RENDER / REVERSE PROXY
# =========================================================

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1
)


# =========================================================
# SESSION CONFIGURATION
# =========================================================

app.config[
    "SESSION_COOKIE_HTTPONLY"
] = True


app.config[
    "SESSION_COOKIE_SAMESITE"
] = SESSION_SAMESITE


app.config[
    "SESSION_COOKIE_SECURE"
] = SESSION_SECURE


app.config[
    "SESSION_REFRESH_EACH_REQUEST"
] = True


app.config[
    "PERMANENT_SESSION_LIFETIME"
] = timedelta(
    days=1
)


# =========================================================
# STATIC FILES
# =========================================================

@app.route(
    "/static/<path:filename>",
    endpoint="static"
)
def static_files(filename):

    return send_from_directory(
        BASE_DIR,
        filename
    )


# =========================================================
# CSS
# =========================================================

@app.route(
    "/css/<path:filename>"
)
def css_files(filename):

    return send_from_directory(
        CSS_DIR,
        filename
    )


# =========================================================
# JAVASCRIPT
# =========================================================

@app.route(
    "/js/<path:filename>"
)
def js_files(filename):

    return send_from_directory(
        JS_DIR,
        filename
    )


# =========================================================
# ASSETS
# =========================================================

@app.route(
    "/assets/<path:filename>"
)
def assets(filename):

    return send_from_directory(
        ASSETS_DIR,
        filename
    )


# =========================================================
# DISCORD API
# =========================================================

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
# DATABASE CONNECTION
# =========================================================

def database_connection():

    if not DATABASE_URL:

        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require"
    )


# =========================================================
# DATABASE SETUP
# =========================================================

def create_database():

    if not DATABASE_URL:

        print(
            "⚠️ Database initialization skipped."
        )

        return

    try:

        with database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS licenses (

                        guild_id BIGINT PRIMARY KEY,

                        license_key TEXT UNIQUE NOT NULL,

                        status TEXT NOT NULL
                            DEFAULT 'active',

                        expires_at TEXT,

                        created_at TEXT NOT NULL

                    )
                    """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS reviews (

                        id SERIAL PRIMARY KEY,

                        user_id TEXT NOT NULL,

                        username TEXT NOT NULL,

                        avatar TEXT,

                        review TEXT NOT NULL,

                        rating INTEGER NOT NULL,

                        created_at TEXT NOT NULL

                    )
                    """
                )

                cursor.execute(
                    """
                    ALTER TABLE reviews
                    ADD COLUMN IF NOT EXISTS avatar TEXT
                    """
                )

                connection.commit()

        print(
            "✅ PostgreSQL database initialized."
        )

    except Exception as error:

        print(
            f"❌ Database initialization error: {error}"
        )


create_database()


# =========================================================
# TIME
# =========================================================

def utc_now():

    return datetime.now(
        timezone.utc
    )


def parse_datetime(value):

    if not value:

        return None

    try:

        parsed = datetime.fromisoformat(
            str(value)
        )

    except (
        ValueError,
        TypeError
    ):

        return None

    if parsed.tzinfo is None:

        parsed = parsed.replace(
            tzinfo=timezone.utc
        )

    return parsed


# =========================================================
# URL VALIDATION
# =========================================================

def safe_next_url(value):

    if not value:

        return "/dashboard"

    value = str(
        value
    )

    if not value.startswith("/"):

        return "/dashboard"

    if value.startswith("//"):

        return "/dashboard"

    return value


# =========================================================
# LICENSE
# =========================================================

def get_license(guild_id):

    try:

        guild_id = int(
            guild_id
        )

    except (
        TypeError,
        ValueError
    ):

        return None

    if not DATABASE_URL:

        return None

    try:

        with database_connection() as connection:

            with connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            ) as cursor:

                cursor.execute(
                    """
                    SELECT
                        guild_id,
                        license_key,
                        status,
                        expires_at,
                        created_at
                    FROM licenses
                    WHERE guild_id = %s
                    LIMIT 1
                    """,
                    (
                        guild_id,
                    )
                )

                row = cursor.fetchone()

                if not row:

                    return None

                return (
                    row["guild_id"],
                    row["license_key"],
                    row["status"],
                    row["expires_at"],
                    row["created_at"]
                )

    except Exception as error:

        print(
            f"❌ License database error: {error}"
        )

        return None


# =========================================================
# GET ALL LICENSES
# =========================================================

def get_all_licenses():

    licenses = {}

    if not DATABASE_URL:

        return licenses

    try:

        with database_connection() as connection:

            with connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            ) as cursor:

                cursor.execute(
                    """
                    SELECT
                        guild_id,
                        license_key,
                        status,
                        expires_at,
                        created_at
                    FROM licenses
                    """
                )

                rows = cursor.fetchall()

                for row in rows:

                    guild_id = str(
                        row["guild_id"]
                    )

                    licenses[guild_id] = (
                        row["guild_id"],
                        row["license_key"],
                        row["status"],
                        row["expires_at"],
                        row["created_at"]
                    )

    except Exception as error:

        print(
            f"❌ Could not load licenses: {error}"
        )

        return {}

    return licenses


# =========================================================
# LICENSE ACTIVE CHECK
# =========================================================

def license_is_active(
    guild_id,
    license_data=None
):

    if license_data is None:

        license_data = get_license(
            guild_id
        )

    if not license_data:

        return False

    status = license_data[2]

    expires_at = license_data[3]

    if status != "active":

        return False

    if expires_at:

        expiration = parse_datetime(
            expires_at
        )

        if not expiration:

            print(
                f"⚠️ Invalid expiration for "
                f"guild {guild_id}: {expires_at}"
            )

            return False

        if utc_now() >= expiration:

            try:

                with database_connection() as connection:

                    with connection.cursor() as cursor:

                        cursor.execute(
                            """
                            UPDATE licenses
                            SET status = 'expired'
                            WHERE guild_id = %s
                            """,
                            (
                                int(guild_id),
                            )
                        )

                    connection.commit()

            except Exception as error:

                print(
                    f"❌ License expiration error: {error}"
                )

            return False

    return True


# =========================================================
# USER HAS ACTIVE LICENSE
# =========================================================

def user_has_license():

    guilds = get_user_guilds()

    if not guilds:

        return False

    licenses = get_all_licenses()

    for guild in guilds:

        guild_id = str(
            guild.get("id", "")
        )

        if not guild_id:

            continue

        license_data = licenses.get(
            guild_id
        )

        if license_is_active(
            guild_id,
            license_data
        ):

            return True

    return False


# =========================================================
# ACTIVE LICENSE IDS
# =========================================================

def get_active_license_guild_ids():

    active_ids = set()

    licenses = get_all_licenses()

    now = utc_now()

    expired_ids = []

    for guild_id, license_data in licenses.items():

        status = license_data[2]

        expires_at = license_data[3]

        if status != "active":

            continue

        if expires_at:

            expiration = parse_datetime(
                expires_at
            )

            if not expiration:

                continue

            if now >= expiration:

                expired_ids.append(
                    guild_id
                )

                continue

        active_ids.add(
            str(guild_id)
        )

    # Expire outdated licenses in one database connection
    if expired_ids:

        try:

            with database_connection() as connection:

                with connection.cursor() as cursor:

                    for guild_id in expired_ids:

                        cursor.execute(
                            """
                            UPDATE licenses
                            SET status = 'expired'
                            WHERE guild_id = %s
                            """,
                            (
                                int(guild_id),
                            )
                        )

                connection.commit()

        except Exception as error:

            print(
                f"❌ Failed to expire licenses: {error}"
            )

    return active_ids


# =========================================================
# DISCORD BOT HEADERS
# =========================================================

def discord_bot_headers():

    if not BOT_TOKEN:

        return {}

    return {

        "Authorization":
            f"Bot {BOT_TOKEN}",

        "Content-Type":
            "application/json"

    }


# =========================================================
# GET USER
# =========================================================

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
# GET USER GUILDS
# =========================================================

def get_user_guilds():

    access_token = session.get(
        "access_token"
    )

    if not access_token:

        return []

    try:

        response = requests.get(

            f"{DISCORD_API}/users/@me/guilds",

            headers={
                "Authorization":
                    f"Bearer {access_token}"
            },

            timeout=10

        )

    except requests.RequestException as error:

        print(
            f"❌ Discord guild request error: {error}"
        )

        return []

    if response.status_code != 200:

        print(
            "❌ Discord guild request returned "
            f"{response.status_code}"
        )

        return []

    try:

        data = response.json()

    except ValueError:

        return []

    if not isinstance(
        data,
        list
    ):

        return []

    return data


# =========================================================
# GET BOT GUILDS
# =========================================================

def get_bot_guilds():

    if not BOT_TOKEN:

        print(
            "⚠️ Discord bot token is missing."
        )

        return []

    try:

        response = requests.get(

            f"{DISCORD_API}/users/@me/guilds",

            headers={
                "Authorization":
                    f"Bot {BOT_TOKEN}"
            },

            timeout=10

        )

    except requests.RequestException as error:

        print(
            f"❌ Bot guild request error: {error}"
        )

        return []

    if response.status_code != 200:

        print(
            f"❌ Bot guild request returned "
            f"{response.status_code}"
        )

        return []

    try:

        data = response.json()

    except ValueError:

        return []

    if not isinstance(
        data,
        list
    ):

        return []

    return data


# =========================================================
# PERMISSIONS
# =========================================================

ADMINISTRATOR = 1 << 3

MANAGE_GUILD = 1 << 5


def can_manage_guild(guild):

    try:

        permissions = int(
            guild.get(
                "permissions",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        permissions = 0

    return bool(

        permissions & ADMINISTRATOR

        or

        permissions & MANAGE_GUILD

    )


# =========================================================
# ADMIN
# =========================================================

def is_admin(user):

    if not user:

        return False

    user_id = str(
        user.get(
            "id",
            ""
        )
    ).strip()

    if not user_id:

        return False

    admin_ids = os.getenv(
        "ADMIN_USER_IDS",
        ""
    )

    if not admin_ids:

        return False

    allowed_ids = {

        item.strip()

        for item in admin_ids.split(",")

        if item.strip()

    }

    return user_id in allowed_ids


# =========================================================
# JINJA TEMPLATE FUNCTIONS
# =========================================================

@app.context_processor
def inject_template_functions():

    return {

        "is_admin":
            is_admin

    }


# =========================================================
# BOT INVITE
# =========================================================

def get_invite_url(guild_id):

    permissions = os.getenv(
        "DISCORD_BOT_PERMISSIONS",
        "0"
    )

    params = {

        "client_id":
            CLIENT_ID,

        "scope":
            "bot applications.commands",

        "permissions":
            permissions,

        "guild_id":
            str(guild_id)

    }

    return (
        f"{DISCORD_OAUTH_URL}?"
        + urlencode(params)
    )


# =========================================================
# OAUTH STATE
# =========================================================

def create_oauth_state():

    state = secrets.token_urlsafe(
        32
    )

    session[
        "oauth_state"
    ] = state

    session[
        "oauth_state_expires_at"
    ] = (
        utc_now()
        + timedelta(minutes=10)
    ).isoformat()

    session.permanent = True
    session.modified = True

    return state


def verify_oauth_state(state):

    if not state:

        print(
            "⚠️ OAuth state verification: "
            "No state received from Discord"
        )

        return False

    stored_state = session.get(
        "oauth_state"
    )

    expires_at_raw = session.get(
        "oauth_state_expires_at"
    )

    print(
        "=========================================="
    )

    print(
        "📋 OAuth State Verification"
    )

    print(
        f"   Received state: {state[:15]}..."
    )

    print(
        f"   Stored state: "
        f"{str(stored_state)[:15] if stored_state else 'NONE'}..."
    )

    print(
        f"   Expiration: {expires_at_raw}"
    )

    if not stored_state:

        print(
            "❌ FAILED: State not in session "
            "(cookie not sent back from Discord)"
        )

        print(
            "=========================================="
        )

        return False

    if expires_at_raw:

        try:

            expires_at = datetime.fromisoformat(
                expires_at_raw
            )

            if expires_at.tzinfo is None:

                expires_at = expires_at.replace(
                    tzinfo=timezone.utc
                )

            if utc_now() >= expires_at:

                print(
                    "❌ FAILED: State expired"
                )

                print(
                    "=========================================="
                )

                session.pop(
                    "oauth_state",
                    None
                )

                session.pop(
                    "oauth_state_expires_at",
                    None
                )

                session.modified = True

                return False

        except ValueError as error:

            print(
                f"❌ FAILED: Date parse error: {error}"
            )

            print(
                "=========================================="
            )

            session.pop(
                "oauth_state",
                None
            )

            session.pop(
                "oauth_state_expires_at",
                None
            )

            session.modified = True

            return False

    if not secrets.compare_digest(
        str(stored_state),
        str(state)
    ):

        print(
            "❌ FAILED: State mismatch "
            "(stored != received)"
        )

        print(
            "=========================================="
        )

        session.pop(
            "oauth_state",
            None
        )

        session.pop(
            "oauth_state_expires_at",
            None
        )

        session.modified = True

        return False

    print(
        "✅ SUCCESS: State validated"
    )

    print(
        "=========================================="
    )

    session.pop(
        "oauth_state",
        None
    )

    session.pop(
        "oauth_state_expires_at",
        None
    )

    session.modified = True

    return True


# =========================================================
# ERROR PAGE
# =========================================================

def error_page(
    title,
    message,
    status_code=400,
    user=None
):

    return render_template(
        "error.html",
        user=user,
        title=title,
        message=message
    ), status_code


# =========================================================
# DISCORD LOGIN
# =========================================================

@app.route("/login")
def login():

    existing_user = get_user()

    if existing_user:

        next_url = safe_next_url(
            request.args.get(
                "next"
            )
            or session.get(
                "next_url"
            )
        )

        session[
            "next_url"
        ] = next_url

        print(
            "✅ User is already logged in."
        )

        print(
            f"👤 User: "
            f"{existing_user.get('username')}"
        )

        print(
            f"➡️ Redirecting to: "
            f"{next_url}"
        )

        return redirect(
            next_url
        )

    if not CLIENT_ID:

        return error_page(
            "❌ Configuration Error",
            "DISCORD_CLIENT_ID is missing.",
            500
        )

    if not CLIENT_SECRET:

        return error_page(
            "❌ Configuration Error",
            "Discord OAuth2 is not configured correctly.",
            500
        )

    if not DISCORD_LOGIN_REDIRECT_URI:

        return error_page(
            "❌ Configuration Error",
            "DISCORD_LOGIN_REDIRECT_URI is missing.",
            500
        )

    next_url = safe_next_url(
        request.args.get(
            "next"
        )
    )

    session[
        "next_url"
    ] = next_url

    state = create_oauth_state()

    params = {

        "client_id":
            CLIENT_ID,

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

        + urlencode(
            params
        )

    )

    print(
        "🔐 Starting Discord LOGIN OAuth2"
    )

    print(
        f"🔗 Login redirect: "
        f"{DISCORD_LOGIN_REDIRECT_URI}"
    )

    print(
        f"➡️ Next: "
        f"{next_url}"
    )

    return redirect(
        discord_url
    )


# =========================================================
# LOGIN CALLBACK
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

        session.pop(
            "oauth_state_expires_at",
            None
        )

        return error_page(
            "❌ OAuth2 Error",
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
            "❌ OAuth2 Error",
            "Invalid or expired OAuth2 state.",
            400
        )

    code = request.args.get(
        "code"
    )

    if not code:

        return error_page(
            "❌ OAuth2 Error",
            "No authorization code was received.",
            400
        )

    if not CLIENT_ID or not CLIENT_SECRET:

        return error_page(
            "❌ Configuration Error",
            "Discord OAuth2 credentials are missing.",
            500
        )

    if not DISCORD_LOGIN_REDIRECT_URI:

        return error_page(
            "❌ Configuration Error",
            "DISCORD_LOGIN_REDIRECT_URI is missing.",
            500
        )

    token_data = {

        "client_id":
            CLIENT_ID,

        "client_secret":
            CLIENT_SECRET,

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
            "❌ OAuth2 Error",
            "Could not contact Discord.",
            500
        )

    if response.status_code != 200:

        print(
            "❌ LOGIN token exchange failed:"
        )

        print(
            response.text
        )

        return error_page(
            "❌ OAuth2 Error",
            "Discord rejected the authorization code.",
            400
        )

    try:

        token_json = response.json()

    except ValueError:

        return error_page(
            "❌ OAuth2 Error",
            "Discord returned an invalid token response.",
            400
        )

    access_token = token_json.get(
        "access_token"
    )

    if not access_token:

        return error_page(
            "❌ OAuth2 Error",
            "Discord did not return an access token.",
            400
        )

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
            f"❌ User request error: {error}"
        )

        return error_page(
            "❌ OAuth2 Error",
            "Failed to retrieve your Discord account.",
            500
        )

    if user_response.status_code != 200:

        return error_page(
            "❌ OAuth2 Error",
            "Failed to verify your Discord account.",
            400
        )

    try:

        user = user_response.json()

    except ValueError:

        return error_page(
            "❌ OAuth2 Error",
            "Discord returned invalid user information.",
            400
        )

    next_url = safe_next_url(
        session.get(
            "next_url"
        )
    )

    session.clear()

    session[
        "access_token"
    ] = access_token

    session[
        "logged_in"
    ] = True

    session[
        "user_id"
    ] = user.get(
        "id"
    )

    session[
        "username"
    ] = user.get(
        "username"
    )

    session[
        "global_name"
    ] = user.get(
        "global_name"
    )

    session.permanent = True

    session.modified = True

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

    print(
        "🚪 User logged out."
    )

    return redirect(
        "/"
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    user = get_user()

    reviews = get_random_reviews(
        6
    )

    return render_template(
        "index.html",
        user=user,
        reviews=reviews
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    user = get_user()

    if not user:

        session[
            "next_url"
        ] = "/dashboard"

        return redirect(
            "/login"
        )

    user_guilds = get_user_guilds()

    bot_guilds = get_bot_guilds()

    bot_guild_ids = {

        str(
            guild.get("id")
        )

        for guild in bot_guilds

        if guild.get("id")

    }

    # =====================================================
    # LOAD ALL LICENSES ONCE
    # =====================================================

    all_licenses = get_all_licenses()

    active_license_ids = set()

    now = utc_now()

    expired_ids = []

    for guild_id, license_data in all_licenses.items():

        status = license_data[2]

        expires_at = license_data[3]

        if status != "active":

            continue

        if expires_at:

            expiration = parse_datetime(
                expires_at
            )

            if not expiration:

                continue

            if now >= expiration:

                expired_ids.append(
                    guild_id
                )

                continue

        active_license_ids.add(
            str(guild_id)
        )

    # =====================================================
    # EXPIRE OLD LICENSES
    # =====================================================

    if expired_ids:

        try:

            with database_connection() as connection:

                with connection.cursor() as cursor:

                    for guild_id in expired_ids:

                        cursor.execute(
                            """
                            UPDATE licenses
                            SET status = 'expired'
                            WHERE guild_id = %s
                            """,
                            (
                                int(guild_id),
                            )
                        )

                connection.commit()

        except Exception as error:

            print(
                f"❌ Failed to expire licenses: {error}"
            )

    authorized = []

    available = []

    for original_guild in user_guilds:

        guild = dict(
            original_guild
        )

        guild_id = str(
            guild.get("id")
        )

        if not guild_id:

            continue

        # =================================================
        # USE ALREADY LOADED LICENSE
        # =================================================

        license_data = all_licenses.get(
            guild_id
        )

        guild[
            "license_data"
        ] = license_data

        guild[
            "license_active"
        ] = (
            guild_id
            in active_license_ids
        )

        if license_data:

            status = license_data[2]

            # If this license expired during this request,
            # expose the new status.
            if guild_id in expired_ids:

                status = "expired"

        else:

            status = "none"

        guild[
            "license_status"
        ] = status

        if guild_id in bot_guild_ids:

            authorized.append(
                guild
            )

            continue

        guild[
            "can_add"
        ] = can_manage_guild(
            guild
        )

        guild[
            "invite_url"
        ] = get_invite_url(
            guild_id
        )

        available.append(
            guild
        )

    authorized.sort(
        key=lambda guild:
            guild.get(
                "name",
                ""
            ).lower()
    )

    available.sort(
        key=lambda guild: (
            not guild.get(
                "can_add",
                False
            ),
            guild.get(
                "name",
                ""
            ).lower()
        )
    )

    return render_template(
        "dashboard.html",
        user=user,
        authorized=authorized,
        available=available
    )


# =========================================================
# MANAGE
# =========================================================

@app.route(
    "/manage/<guild_id>"
)
def manage(guild_id):

    user = get_user()

    if not user:

        session[
            "next_url"
        ] = f"/manage/{guild_id}"

        return redirect(
            "/login"
        )

    user_guilds = get_user_guilds()

    guild = next(

        (

            guild

            for guild in user_guilds

            if str(
                guild.get("id")
            ) == str(guild_id)

        ),

        None

    )

    if guild is None:

        return error_page(
            "❌ Access denied",
            "You are not a member of this server.",
            403,
            user
        )

    bot_guilds = get_bot_guilds()

    bot_guild_ids = {

        str(
            g.get("id")
        )

        for g in bot_guilds

        if g.get("id")

    }

    if str(guild_id) not in bot_guild_ids:

        return redirect(
            "/dashboard"
        )

    license_data = get_license(
        guild_id
    )

    license_active = license_is_active(
        guild_id,
        license_data
    )

    return render_template(
        "manage.html",
        user=user,
        guild=guild,
        license_data=license_data,
        license_active=license_active
    )


# =========================================================
# REVIEWS DATABASE
# =========================================================

def get_random_reviews(
    amount=6
):

    if not DATABASE_URL:

        return []

    try:

        with database_connection() as connection:

            with connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            ) as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        user_id,
                        username,
                        avatar,
                        review,
                        rating,
                        created_at
                    FROM reviews
                    ORDER BY id DESC
                    """
                )

                rows = cursor.fetchall()

    except Exception as error:

        print(
            f"❌ Reviews database error: {error}"
        )

        return []

    reviews = []

    for row in rows:

        reviews.append({

            "id":
                row["id"],

            "user_id":
                row["user_id"],

            "username":
                row["username"],

            "avatar":
                row["avatar"],

            "review":
                row["review"],

            "rating":
                row["rating"],

            "created_at":
                row["created_at"]

        })

    random.shuffle(
        reviews
    )

    return reviews[:amount]


# =========================================================
# REVIEWS PAGE
# =========================================================

@app.route("/reviews")
def reviews():

    user = get_user()

    review_list = get_random_reviews(
        12
    )

    can_review = False

    if user:

        can_review = user_has_license()

    return render_template(
        "reviews.html",
        user=user,
        review_list=review_list,
        can_review=can_review
    )


# =========================================================
# SUBMIT REVIEW
# =========================================================

@app.route(
    "/reviews",
    methods=["POST"]
)
def submit_review():

    user = get_user()

    if not user:

        session[
            "next_url"
        ] = "/reviews"

        return redirect(
            "/login"
        )

    if not user_has_license():

        return error_page(
            "🔒 License required",
            "Only users with an active Misuki license can submit reviews.",
            403,
            user
        )

    review = request.form.get(
        "review",
        ""
    ).strip()

    rating_raw = request.form.get(
        "rating",
        "5"
    )

    try:

        rating = int(
            rating_raw
        )

    except (
        ValueError,
        TypeError
    ):

        rating = 5

    rating = max(
        1,
        min(
            5,
            rating
        )
    )

    if not review:

        return redirect(
            "/reviews"
        )

    review = review[:1000]

    user_id = str(
        user.get(
            "id"
        )
    )

    username = (

        user.get(
            "global_name"
        )

        or

        user.get(
            "username"
        )

        or

        "Discord User"

    )

    avatar_hash = user.get(
        "avatar"
    )

    if avatar_hash:

        avatar = (

            "https://cdn.discordapp.com/"

            f"avatars/{user_id}/"

            f"{avatar_hash}.png?size=128"

        )

    else:

        avatar = None

    if not DATABASE_URL:

        return error_page(
            "❌ Review Error",
            "The database is not configured.",
            500,
            user
        )

    try:

        with database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(

                    """
                    INSERT INTO reviews
                    (
                        user_id,
                        username,
                        avatar,
                        review,
                        rating,
                        created_at
                    )

                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,

                    (

                        user_id,

                        username,

                        avatar,

                        review,

                        rating,

                        utc_now().isoformat()

                    )

                )

            connection.commit()

    except Exception as error:

        print(
            f"❌ Review insert error: {error}"
        )

        return error_page(
            "❌ Review Error",
            "The review could not be saved.",
            500,
            user
        )

    return redirect(
        "/reviews"
    )


# =========================================================
# DOCUMENTATION
# =========================================================

@app.route("/documentation")
def documentation():

    user = get_user()

    return render_template(
        "documentation.html",
        user=user
    )


# =========================================================
# SUPPORT
# =========================================================

@app.route("/support")
def support():

    user = get_user()

    return render_template(
        "support.html",
        user=user
    )


# =========================================================
# TERMS
# =========================================================

@app.route("/terms")
def terms():

    user = get_user()

    return render_template(
        "terms.html",
        user=user
    )


# =========================================================
# PRIVACY
# =========================================================

@app.route("/privacy")
def privacy():

    user = get_user()

    return render_template(
        "privacy.html",
        user=user
    )


# =========================================================
# DATA
# =========================================================

@app.route("/data")
def data_page():

    user = get_user()

    return render_template(
        "data.html",
        user=user
    )


# =========================================================
# COOKIES
# =========================================================

@app.route("/cookies")
def cookies_page():

    user = get_user()

    return render_template(
        "cookies.html",
        user=user
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    print(
        "=========================================="
    )

    print(
        "🌐 Misuki OAuth2 Web Server"
    )

    print(
        "=========================================="
    )

    print(
        f"🌐 Port: {PORT}"
    )

    print(
        f"🔐 Client ID configured: "
        f"{bool(CLIENT_ID)}"
    )

    print(
        f"🔑 Client Secret configured: "
        f"{bool(CLIENT_SECRET)}"
    )

    print(
        f"🤖 Bot Token configured: "
        f"{bool(BOT_TOKEN)}"
    )

    print(
        f"🗄️ PostgreSQL configured: "
        f"{bool(DATABASE_URL)}"
    )

    print(
        f"🔐 Login Redirect: "
        f"{DISCORD_LOGIN_REDIRECT_URI}"
    )

    print(
        f"🛡️ Admin IDs configured: "
        f"{bool(os.getenv('ADMIN_USER_IDS'))}"
    )

    print(
        f"🗝️ Persistent Flask Secret: "
        f"{bool(os.getenv('FLASK_SECRET_KEY'))}"
    )

    print(
        f"🍪 Active Session Config: "
        f"SameSite={SESSION_SAMESITE}, "
        f"Secure={SESSION_SECURE}"
    )

    print(
        "=========================================="
    )

    app.run(

        host="0.0.0.0",

        port=PORT,

        debug=False

    )

