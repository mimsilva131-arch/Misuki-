
import os
import random
import secrets

from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode, urlparse

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
# CONFIGURATION
# =========================================================

CLIENT_ID = os.getenv(
    "DISCORD_CLIENT_ID"
)

CLIENT_SECRET = os.getenv(
    "DISCORD_CLIENT_SECRET"
)

# Mantido para compatibilidade com outras partes.
# O LOGIN usa exclusivamente DISCORD_LOGIN_REDIRECT_URI.
DISCORD_REDIRECT_URI = os.getenv(
    "DISCORD_REDIRECT_URI"
)

DISCORD_LOGIN_REDIRECT_URI = os.getenv(
    "DISCORD_LOGIN_REDIRECT_URI"
)

BOT_TOKEN = (
    os.getenv("DISCORD_BOT_TOKEN")
    or os.getenv("DISCORD_TOKEN")
)

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

SECRET_KEY = os.getenv(
    "FLASK_SECRET_KEY"
)

PORT = int(
    os.getenv(
        "PORT",
        "5000"
    )
)

COOKIE_SECURE = (
    os.getenv(
        "COOKIE_SECURE",
        "true"
    ).lower()
    == "true"
)


# =========================================================
# ADMIN CONFIGURATION
# =========================================================

ADMIN_DISCORD_IDS = {
    str(user_id).strip()
    for user_id in os.getenv(
        "ADMIN_DISCORD_IDS",
        ""
    ).split(",")
    if user_id.strip()
}


def is_admin(user=None):

    if user is None:
        user = get_user()

    if not user:
        return False

    return str(
        user.get("id")
    ) in ADMIN_DISCORD_IDS


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
# FLASK
# =========================================================

app = Flask(
    __name__,
    template_folder=WEBSITE_DIR,
    static_folder=BASE_DIR,
    static_url_path="/static"
)

app.secret_key = SECRET_KEY

app.config["PROPAGATE_EXCEPTIONS"] = True

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
app.config["SESSION_COOKIE_SECURE"] = COOKIE_SECURE
app.config["SESSION_REFRESH_EACH_REQUEST"] = True

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    days=1
)


# =========================================================
# STATIC CSS
# =========================================================

@app.route("/css/<path:filename>")
def static_css(filename):

    return send_from_directory(
        CSS_DIR,
        filename
    )


# =========================================================
# STATIC JAVASCRIPT
# =========================================================

@app.route("/js/<path:filename>")
def static_js(filename):

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
# DATABASE
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

                # -------------------------------------------------
                # LICENSES
                # -------------------------------------------------

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

                # -------------------------------------------------
                # REVIEWS
                # -------------------------------------------------

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

                # -------------------------------------------------
                # ADVERTISEMENTS
                # -------------------------------------------------

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS advertisements (

                        id SERIAL PRIMARY KEY,

                        user_id TEXT NOT NULL,

                        username TEXT NOT NULL,

                        title TEXT NOT NULL,

                        description TEXT NOT NULL,

                        image_url TEXT,

                        target_url TEXT NOT NULL,

                        status TEXT NOT NULL
                            DEFAULT 'pending',

                        rejection_reason TEXT,

                        duration_days INTEGER NOT NULL
                            DEFAULT 7,

                        start_at TEXT,

                        end_at TEXT,

                        created_at TEXT NOT NULL,

                        updated_at TEXT NOT NULL

                    )
                    """
                )

                # -------------------------------------------------
                # ADVERTISEMENTS MIGRATION
                # -------------------------------------------------

                cursor.execute(
                    """
                    ALTER TABLE advertisements
                    ADD COLUMN IF NOT EXISTS duration_days
                    INTEGER NOT NULL DEFAULT 7
                    """
                )

                # -------------------------------------------------
                # ADVERTISEMENT PAYMENTS
                # -------------------------------------------------

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS advertisement_payments (

                        id SERIAL PRIMARY KEY,

                        advertisement_id INTEGER
                            REFERENCES advertisements(id)
                            ON DELETE CASCADE,

                        user_id TEXT NOT NULL,

                        provider TEXT NOT NULL
                            DEFAULT 'paypal',

                        provider_payment_id TEXT,

                        amount NUMERIC(10, 2),

                        currency TEXT
                            DEFAULT 'EUR',

                        status TEXT NOT NULL
                            DEFAULT 'not_configured',

                        created_at TEXT NOT NULL,

                        updated_at TEXT NOT NULL

                    )
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

def valid_http_url(value):

    if not value:
        return False

    try:

        parsed = urlparse(
            str(value).strip()
        )

    except Exception:

        return False

    return (
        parsed.scheme.lower()
        in ("http", "https")
        and bool(parsed.netloc)
    )


def safe_next_url(value):

    if not value:
        return "/dashboard"

    value = str(value)

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
# LICENSE ACTIVE CHECK
# =========================================================

def license_is_active(guild_id):

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
# USER GUILDS
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
        return []

    try:

        data = response.json()

    except ValueError:

        return []

    return data if isinstance(
        data,
        list
    ) else []


# =========================================================
# USER HAS ACTIVE LICENSE
# =========================================================

def user_has_license():

    guilds = get_user_guilds()

    for guild in guilds:

        guild_id = guild.get(
            "id"
        )

        if guild_id and license_is_active(
            guild_id
        ):

            return True

    return False


# =========================================================
# ACTIVE LICENSE IDS
# =========================================================

def get_active_license_guild_ids():

    active_ids = set()

    if not DATABASE_URL:
        return active_ids

    try:

        with database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        guild_id,
                        status,
                        expires_at
                    FROM licenses
                    """
                )

                rows = cursor.fetchall()

    except Exception as error:

        print(
            f"❌ Could not load licenses: {error}"
        )

        return active_ids

    now = utc_now()

    for row in rows:

        guild_id = row[0]
        status = row[1]
        expires_at = row[2]

        if status != "active":
            continue

        if expires_at:

            expiration = parse_datetime(
                expires_at
            )

            if not expiration:
                continue

            if now >= expiration:

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

                except Exception:
                    pass

                continue

        active_ids.add(
            str(guild_id)
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

    except requests.RequestException:

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
# GET BOT GUILDS
# =========================================================

def get_bot_guilds():

    if not BOT_TOKEN:
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

    except requests.RequestException:

        return []

    if response.status_code != 200:
        return []

    try:

        data = response.json()

    except ValueError:

        return []

    return data if isinstance(
        data,
        list
    ) else []


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

    session["oauth_state"] = state

    session.modified = True

    return state


def verify_oauth_state(state):

    stored_state = session.pop(
        "oauth_state",
        None
    )

    session.modified = True

    if not state or not stored_state:
        return False

    return secrets.compare_digest(
        str(stored_state),
        str(state)
    )


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
# LOGIN
# =========================================================

@app.route("/login")
def login():

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

    session["next_url"] = next_url

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
        + urlencode(params)
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

        return error_page(
            "❌ OAuth2 Error",
            f"Discord returned an OAuth error: {error}",
            400
        )

    code = request.args.get(
        "code"
    )

    state = request.args.get(
        "state"
    )

    if not code:

        return error_page(
            "❌ OAuth2 Error",
            "No authorization code was received.",
            400
        )

    if not verify_oauth_state(
        state
    ):

        return error_page(
            "❌ OAuth2 Error",
            "Invalid OAuth state. Please try logging in again.",
            400
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

    except requests.RequestException:

        return error_page(
            "❌ OAuth2 Error",
            "Could not contact Discord.",
            500
        )

    if response.status_code != 200:

        print(
            "❌ Discord token response:",
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

    except requests.RequestException:

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
            "Discord returned invalid user data.",
            400
        )

    next_url = safe_next_url(
        session.get(
            "next_url"
        )
    )

    session.clear()

    session["access_token"] = access_token
    session["logged_in"] = True
    session["user_id"] = user.get(
        "id"
    )

    session["username"] = (
        user.get("global_name")
        or
        user.get("username")
    )

    session.permanent = True
    session.modified = True

    return redirect(
        next_url
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================================================
# REVIEWS
# =========================================================

def get_random_reviews(amount=6):

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
# ADVERTISEMENTS
# =========================================================

def get_active_advertisements():

    if not DATABASE_URL:
        return []

    expire_advertisements()

    now = utc_now().isoformat()

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
                        title,
                        description,
                        image_url,
                        target_url,
                        status,
                        duration_days,
                        start_at,
                        end_at,
                        created_at
                    FROM advertisements
                    WHERE status = 'active'
                    AND (
                        start_at IS NULL
                        OR start_at <= %s
                    )
                    AND (
                        end_at IS NULL
                        OR end_at > %s
                    )
                    ORDER BY id DESC
                    """,
                    (
                        now,
                        now
                    )
                )

                return cursor.fetchall()

    except Exception as error:

        print(
            f"❌ Advertisement database error: {error}"
        )

        return []


def expire_advertisements():

    if not DATABASE_URL:
        return

    now = utc_now().isoformat()

    try:

        with database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE advertisements
                    SET
                        status = 'expired',
                        updated_at = %s
                    WHERE status = 'active'
                    AND end_at IS NOT NULL
                    AND end_at <= %s
                    """,
                    (
                        now,
                        now
                    )
                )

            connection.commit()

    except Exception as error:

        print(
            f"❌ Advertisement expiration error: {error}"
        )


def get_all_advertisements():

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
                        title,
                        description,
                        image_url,
                        target_url,
                        status,
                        rejection_reason,
                        duration_days,
                        start_at,
                        end_at,
                        created_at,
                        updated_at
                    FROM advertisements
                    ORDER BY id DESC
                    """
                )

                return cursor.fetchall()

    except Exception as error:

        print(
            f"❌ Could not load advertisements: {error}"
        )

        return []


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    user = get_user()

    expire_advertisements()

    reviews = get_random_reviews(
        6
    )

    advertisements = (
        get_active_advertisements()
    )

    return render_template(
        "index.html",
        user=user,
        reviews=reviews,
        advertisements=advertisements
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

        return redirect("/login")

    user_guilds = get_user_guilds()

    bot_guilds = get_bot_guilds()

    bot_guild_ids = {
        str(guild.get("id"))
        for guild in bot_guilds
        if guild.get("id")
    }

    active_license_ids = (
        get_active_license_guild_ids()
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

        license_data = get_license(
            guild_id
        )

        guild["license_data"] = (
            license_data
        )

        guild["license_active"] = (
            guild_id in active_license_ids
        )

        if license_data:

            status = license_data[2]

        else:

            status = "none"

        guild["license_status"] = (
            status
        )

        if guild_id in bot_guild_ids:

            authorized.append(
                guild
            )

            continue

        guild["can_add"] = (
            can_manage_guild(
                guild
            )
        )

        guild["invite_url"] = (
            get_invite_url(
                guild_id
            )
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

@app.route("/manage/<guild_id>")
def manage(guild_id):

    user = get_user()

    if not user:

        session["next_url"] = (
            f"/manage/{guild_id}"
        )

        return redirect("/login")

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
        str(g.get("id"))
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
        guild_id
    )

    return render_template(
        "manage.html",
        user=user,
        guild=guild,
        license_data=license_data,
        license_active=license_active
    )


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

        can_review = (
            user_has_license()
        )

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

        session["next_url"] = (
            "/reviews"
        )

        return redirect("/login")

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
        user.get("id")
    )

    username = (
        user.get("global_name")
        or
        user.get("username")
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
# ADVERTISE PAGE
# =========================================================

@app.route("/advertise")
def advertise():

    user = get_user()

    if not user:

        session["next_url"] = (
            "/advertise"
        )

        return redirect("/login")

    return render_template(
        "advertise.html",
        user=user
    )


# =========================================================
# CREATE ADVERTISEMENT
# =========================================================

@app.route(
    "/advertise",
    methods=["POST"]
)
def create_advertisement():

    user = get_user()

    if not user:

        session["next_url"] = (
            "/advertise"
        )

        return redirect("/login")

    title = request.form.get(
        "title",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    image_url = request.form.get(
        "image_url",
        ""
    ).strip()

    target_url = request.form.get(
        "target_url",
        ""
    ).strip()

    duration_raw = request.form.get(
        "duration",
        "7"
    ).strip()

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not title:

        return error_page(
            "❌ Invalid advertisement",
            "The advertisement needs a title.",
            400,
            user
        )

    if not description:

        return error_page(
            "❌ Invalid advertisement",
            "The advertisement needs a description.",
            400,
            user
        )

    if not target_url or not valid_http_url(
        target_url
    ):

        return error_page(
            "❌ Invalid URL",
            "Please provide a valid HTTP or HTTPS destination URL.",
            400,
            user
        )

    if image_url and not valid_http_url(
        image_url
    ):

        return error_page(
            "❌ Invalid image URL",
            "The image URL must use HTTP or HTTPS.",
            400,
            user
        )

    # -----------------------------------------------------
    # DURATION
    # -----------------------------------------------------

    try:

        duration = int(
            duration_raw
        )

    except (
        ValueError,
        TypeError
    ):

        return error_page(
            "❌ Invalid duration",
            "The advertisement duration is invalid.",
            400,
            user
        )

    if duration not in (
        7,
        14,
        30
    ):

        return error_page(
            "❌ Invalid duration",
            "The advertisement duration must be 7, 14 or 30 days.",
            400,
            user
        )

    # -----------------------------------------------------
    # LIMITS
    # -----------------------------------------------------

    title = title[:100]

    description = description[:500]

    target_url = target_url[:1000]

    image_url = (
        image_url[:1000]
        if image_url
        else None
    )

    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------

    user_id = str(
        user.get("id")
    )

    username = (
        user.get("global_name")
        or
        user.get("username")
        or
        "Discord User"
    )

    now = utc_now().isoformat()

    # -----------------------------------------------------
    # DATABASE CHECK
    # -----------------------------------------------------

    if not DATABASE_URL:

        return error_page(
            "❌ Database error",
            "The database is not configured.",
            500,
            user
        )

    # =====================================================
    # CREATE ADVERTISEMENT
    # =====================================================

    try:

        with database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO advertisements
                    (
                        user_id,
                        username,
                        title,
                        description,
                        image_url,
                        target_url,
                        status,
                        rejection_reason,
                        duration_days,
                        start_at,
                        end_at,
                        created_at,
                        updated_at
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        'pending',
                        NULL,
                        %s,
                        NULL,
                        NULL,
                        %s,
                        %s
                    )
                    RETURNING id
                    """,
                    (
                        user_id,
                        username,
                        title,
                        description,
                        image_url,
                        target_url,
                        duration,
                        now,
                        now
                    )
                )

                result = cursor.fetchone()

                if not result:

                    raise RuntimeError(
                        "Advertisement ID was not returned."
                    )

                advertisement_id = result[0]

            connection.commit()

    except Exception as error:

        print(
            f"❌ Advertisement creation error: {error}"
        )

        return error_page(
            "❌ Advertisement Error",
            "The advertisement could not be created.",
            500,
            user
        )

    # =====================================================
    # PAYMENT RECORD
    # =====================================================

    try:

        with database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO advertisement_payments
                    (
                        advertisement_id,
                        user_id,
                        provider,
                        provider_payment_id,
                        amount,
                        currency,
                        status,
                        created_at,
                        updated_at
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        'paypal',
                        NULL,
                        NULL,
                        'EUR',
                        'not_configured',
                        %s,
                        %s
                    )
                    """,
                    (
                        advertisement_id,
                        user_id,
                        now,
                        now
                    )
                )

            connection.commit()

    except Exception as error:

        print(
            f"⚠️ Advertisement payment record error: {error}"
        )

    # =====================================================
    # SUCCESS
    # =====================================================

    return render_template(
        "advertise_success.html",
        user=user
    )


# =========================================================
# ADMIN ADVERTISEMENT PANEL
# =========================================================

@app.route(
    "/admin/advertisements"
)
def admin_advertisements():

    user = get_user()

    if not user:

        session["next_url"] = (
            "/admin/advertisements"
        )

        return redirect("/login")

    if not is_admin(user):

        return error_page(
            "🚫 Access denied",
            "You do not have permission to access the advertisement administration panel.",
            403,
            user
        )

    expire_advertisements()

    advertisements = (
        get_all_advertisements()
    )

    return render_template(
        "admin_advertisements.html",
        user=user,
        advertisements=advertisements
    )


# =========================================================
# ADMIN APPROVE ADVERTISEMENT
# =========================================================

@app.route(
    "/admin/advertisements/<int:advertisement_id>/approve",
    methods=["POST"]
)
def approve_advertisement(
    advertisement_id
):

    user = get_user()

    if not user:

        return redirect(
            "/login"
        )

    if not is_admin(user):

        return error_page(
            "🚫 Access denied",
            "You do not have permission to approve advertisements.",
            403,
            user
        )

    if not DATABASE_URL:

        return error_page(
            "❌ Database error",
            "The database is not configured.",
            500,
            user
        )

    now = utc_now()

    # -----------------------------------------------------
    # GET ADVERTISEMENT
    # -----------------------------------------------------

    try:

        with database_connection() as connection:

            with connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            ) as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        duration_days
                    FROM advertisements
                    WHERE id = %s
                    LIMIT 1
                    """,
                    (
                        advertisement_id,
                    )
                )

                advertisement = (
                    cursor.fetchone()
                )

    except Exception as error:

        print(
            f"❌ Advertisement lookup error: {error}"
        )

        return error_page(
            "❌ Advertisement Error",
            "The advertisement could not be loaded.",
            500,
            user
        )

    if not advertisement:

        return error_page(
            "❌ Advertisement not found",
            "This advertisement does not exist.",
            404,
            user
        )

    # -----------------------------------------------------
    # DURATION
    # -----------------------------------------------------

    try:

        duration_days = int(
            advertisement[
                "duration_days"
            ]
        )

    except (
        ValueError,
        TypeError
    ):

        duration_days = 7

    if duration_days not in (
        7,
        14,
        30
    ):

        duration_days = 7

    # -----------------------------------------------------
    # CALCULATE END
    # -----------------------------------------------------

    start_at = now

    end_at = (
        start_at
        +
        timedelta(
            days=duration_days
        )
    )

    # -----------------------------------------------------
    # ACTIVATE
    # -----------------------------------------------------

    try:

        with database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE advertisements
                    SET
                        status = 'active',
                        rejection_reason = NULL,
                        start_at = %s,
                        end_at = %s,
                        updated_at = %s
                    WHERE id = %s
                    """,
                    (
                        start_at.isoformat(),
                        end_at.isoformat(),
                        now.isoformat(),
                        advertisement_id
                    )
                )

            connection.commit()

    except Exception as error:

        print(
            f"❌ Advertisement approval error: {error}"
        )

        return error_page(
            "❌ Advertisement Error",
            "The advertisement could not be approved.",
            500,
            user
        )

    return redirect(
        "/admin/advertisements"
    )


# =========================================================
# ADMIN REJECT ADVERTISEMENT
# =========================================================

@app.route(
    "/admin/advertisements/<int:advertisement_id>/reject",
    methods=["POST"]
)
def reject_advertisement(
    advertisement_id
):

    user = get_user()

    if not user:

        return redirect(
            "/login"
        )

    if not is_admin(user):

        return error_page(
            "🚫 Access denied",
            "You do not have permission to reject advertisements.",
            403,
            user
        )

    reason = request.form.get(
        "reason",
        ""
    ).strip()

    reason = reason[:500]

    now = utc_now().isoformat()

    try:

        with database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE advertisements
                    SET
                        status = 'rejected',
                        rejection_reason = %s,
                        updated_at = %s
                    WHERE id = %s
                    """,
                    (
                        reason
                        or
                        "Rejected by administrator.",
                        now,
                        advertisement_id
                    )
                )

            connection.commit()

    except Exception as error:

        print(
            f"❌ Advertisement rejection error: {error}"
        )

        return error_page(
            "❌ Advertisement Error",
            "The advertisement could not be rejected.",
            500,
            user
        )

    return redirect(
        "/admin/advertisements"
    )


# =========================================================
# ADMIN DISABLE ADVERTISEMENT
# =========================================================

@app.route(
    "/admin/advertisements/<int:advertisement_id>/disable",
    methods=["POST"]
)
def disable_advertisement(
    advertisement_id
):

    user = get_user()

    if not user:

        return redirect(
            "/login"
        )

    if not is_admin(user):

        return error_page(
            "🚫 Access denied",
            "You do not have permission to disable advertisements.",
            403,
            user
        )

    now = utc_now().isoformat()

    try:

        with database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE advertisements
                    SET
                        status = 'disabled',
                        updated_at = %s
                    WHERE id = %s
                    """,
                    (
                        now,
                        advertisement_id
                    )
                )

            connection.commit()

    except Exception as error:

        print(
            f"❌ Advertisement disable error: {error}"
        )

        return error_page(
            "❌ Advertisement Error",
            "The advertisement could not be disabled.",
            500,
            user
        )

    return redirect(
        "/admin/advertisements"
    )


# =========================================================
# DOCUMENTATION
# =========================================================

@app.route(
    "/documentation"
)
def documentation():

    return render_template(
        "documentation.html"
    )


# =========================================================
# SUPPORT
# =========================================================

@app.route(
    "/support"
)
def support():

    return render_template(
        "support.html"
    )


# =========================================================
# TERMS
# =========================================================

@app.route(
    "/terms"
)
def terms():

    return render_template(
        "terms.html"
    )


# =========================================================
# PRIVACY
# =========================================================

@app.route(
    "/privacy"
)
def privacy():

    return render_template(
        "privacy.html"
    )


# =========================================================
# DATA
# =========================================================

@app.route(
    "/data"
)
def data_page():

    return render_template(
        "data.html"
    )


# =========================================================
# COOKIES
# =========================================================

@app.route(
    "/cookies"
)
def cookies_page():

    return render_template(
        "cookies.html"
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route(
    "/health"
)
def health():

    return {
        "status": "ok",
        "database": bool(
            DATABASE_URL
        ),
        "discord": bool(
            CLIENT_ID
        ),
        "bot": bool(
            BOT_TOKEN
        )
    }, 200


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
        f"👑 Admin IDs configured: "
        f"{len(ADMIN_DISCORD_IDS)}"
    )

    print(
        f"🔐 Login Redirect: "
        f"{DISCORD_LOGIN_REDIRECT_URI}"
    )

    print(
        f"🗝️ Persistent Flask Secret: "
        f"{bool(os.getenv('FLASK_SECRET_KEY'))}"
    )

    print(
        f"🍪 Secure Cookies: "
        f"{COOKIE_SECURE}"
    )

    print(
        "=========================================="
    )

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False
    )

