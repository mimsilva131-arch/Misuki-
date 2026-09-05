import os
import random
import secrets
import time
import hashlib
import hmac
import json

from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import requests
import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

from flask import (
    Flask,
    redirect,
    session,
    request,
    render_template,
    send_from_directory,
    jsonify
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

SESSION_SAMESITE = "Lax"

SESSION_SECURE = (
    os.getenv(
        "SESSION_COOKIE_SECURE",
        "false"
    ).lower()
    == "true"
)


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
] = False

app.config[
    "PERMANENT_SESSION_LIFETIME"
] = timedelta(
    days=1
)


# =========================================================
# HTTP SESSION
# =========================================================

discord_http = requests.Session()


# =========================================================
# DATABASE CONNECTION POOL
# =========================================================

db_pool = None


if DATABASE_URL:

    try:

        db_pool = ThreadedConnectionPool(
            1,
            10,
            DATABASE_URL,
            sslmode="require"
        )

        print(
            "✅ PostgreSQL connection pool created."
        )

    except Exception as error:

        print(
            f"❌ PostgreSQL pool error: {error}"
        )

        db_pool = None


# =========================================================
# DATABASE CONNECTION CONTEXT
# =========================================================

@contextmanager
def database_connection():

    if not db_pool:

        raise RuntimeError(
            "PostgreSQL connection pool is not available."
        )

    connection = None

    try:

        connection = db_pool.getconn()

        yield connection

    except Exception:

        if connection:

            try:
                connection.rollback()
            except Exception:
                pass

        raise

    finally:

        if connection:

            try:

                db_pool.putconn(
                    connection
                )

            except Exception as error:

                print(
                    f"❌ Failed to return "
                    f"database connection: {error}"
                )


# =========================================================
# STATIC FILES
# =========================================================

@app.route(
    "/static/<path:filename>",
    endpoint="static"
)
def static_files(filename):

    root_file = os.path.join(
        BASE_DIR,
        filename
    )

    if os.path.isfile(root_file):

        return send_from_directory(
            BASE_DIR,
            filename
        )

    return send_from_directory(
        os.path.join(BASE_DIR, "static"),
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
# DATABASE SETUP
# =========================================================

def create_database():

    if not DATABASE_URL or not db_pool:

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

                # -------------------------------------------------
                # VERIFICATION REQUESTS
                # -------------------------------------------------

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS verification_requests (

                        id BIGSERIAL PRIMARY KEY,

                        guild_id BIGINT NOT NULL,

                        user_id BIGINT NOT NULL,

                        username TEXT,

                        status TEXT NOT NULL
                            DEFAULT 'pending',

                        created_at DOUBLE PRECISION NOT NULL,

                        processed_at DOUBLE PRECISION,

                        failure_reason TEXT,

                        UNIQUE (
                            guild_id,
                            user_id
                        )
                    )
                    """
                )

                cursor.execute(
                    """
                    ALTER TABLE verification_requests
                    ADD COLUMN IF NOT EXISTS failure_reason TEXT
                    """
                )

                # -------------------------------------------------
                # VERIFICATION CAPTCHAS
                # -------------------------------------------------

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS verification_captchas (

                        id BIGSERIAL PRIMARY KEY,

                        token TEXT UNIQUE NOT NULL,

                        guild_id BIGINT NOT NULL,

                        user_id BIGINT NOT NULL,

                        question TEXT NOT NULL,

                        answer_hash TEXT NOT NULL,

                        created_at DOUBLE PRECISION NOT NULL,

                        expires_at DOUBLE PRECISION NOT NULL,

                        attempts INTEGER NOT NULL
                            DEFAULT 0,

                        used BOOLEAN NOT NULL
                            DEFAULT FALSE
                    )
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    verification_captchas_user_idx

                    ON verification_captchas (
                        guild_id,
                        user_id
                    )
                    """
                )

                # -------------------------------------------------
                # BOT STATISTICS
                # -------------------------------------------------

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS bot_statistics (

                        id INTEGER PRIMARY KEY,

                        servers INTEGER NOT NULL
                            DEFAULT 0,

                        users INTEGER NOT NULL
                            DEFAULT 0,

                        channels INTEGER NOT NULL
                            DEFAULT 0,

                        latency INTEGER NOT NULL
                            DEFAULT 0,

                        commands INTEGER NOT NULL
                            DEFAULT 0,

                        verifications INTEGER NOT NULL
                            DEFAULT 0,

                        bot_status TEXT NOT NULL
                            DEFAULT 'Offline',

                        uptime TEXT NOT NULL
                            DEFAULT '0s',

                        version TEXT NOT NULL
                            DEFAULT '1.0.0',

                        last_seen DOUBLE PRECISION,

                        admin_servers JSONB NOT NULL
                            DEFAULT '[]'::jsonb,

                        updated_at DOUBLE PRECISION NOT NULL
                            DEFAULT 0
                    )
                    """
                )

                cursor.execute(
                    """
                    ALTER TABLE bot_statistics
                    ADD COLUMN IF NOT EXISTS verifications INTEGER
                    NOT NULL DEFAULT 0
                    """
                )

                cursor.execute(
                    """
                    ALTER TABLE bot_statistics
                    ADD COLUMN IF NOT EXISTS last_seen DOUBLE PRECISION
                    """
                )

                cursor.execute(
                    """
                    ALTER TABLE bot_statistics
                    ADD COLUMN IF NOT EXISTS admin_servers JSONB
                    NOT NULL DEFAULT '[]'::jsonb
                    """
                )

                cursor.execute(
                    """
                    ALTER TABLE bot_statistics
                    ADD COLUMN IF NOT EXISTS updated_at DOUBLE PRECISION
                    NOT NULL DEFAULT 0
                    """
                )

                cursor.execute(
                    """
                    INSERT INTO bot_statistics (
                        id,
                        servers,
                        users,
                        channels,
                        latency,
                        commands,
                        verifications,
                        bot_status,
                        uptime,
                        version,
                        last_seen,
                        admin_servers,
                        updated_at
                    )

                    VALUES (
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        'Offline',
                        '0s',
                        '1.0.0',
                        NULL,
                        '[]'::jsonb,
                        0
                    )

                    ON CONFLICT (id)
                    DO NOTHING
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

    if not DATABASE_URL or not db_pool:

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

    if not DATABASE_URL or not db_pool:

        return {}

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

        licenses = {}

        now = utc_now()

        for row in rows:

            guild_id = str(
                row["guild_id"]
            )

            status = row["status"]

            expires_at = row["expires_at"]

            if (
                status == "active"
                and expires_at
            ):

                expiration = parse_datetime(
                    expires_at
                )

                if expiration and now >= expiration:

                    status = "expired"

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

            licenses[guild_id] = {

                "guild_id":
                    row["guild_id"],

                "license_key":
                    row["license_key"],

                "status":
                    status,

                "expires_at":
                    expires_at,

                "created_at":
                    row["created_at"]

            }

        return licenses

    except Exception as error:

        print(
            f"❌ Could not load licenses: {error}"
        )

        return {}


LICENSE_SYSTEM_ENABLED = False


# =========================================================
# LICENSE ACTIVE CHECK
# =========================================================

def license_is_active(guild_id):

    if not LICENSE_SYSTEM_ENABLED:

        return True

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
# USER HAS ACTIVE LICENSE
# =========================================================

def user_has_license():

    guilds = get_user_guilds()

    if not guilds:

        return False

    licenses = get_all_licenses()

    for guild in guilds:

        guild_id = str(
            guild.get(
                "id",
                ""
            )
        )

        license_data = licenses.get(
            guild_id
        )

        if not license_data:

            continue

        if license_data["status"] != "active":

            continue

        expires_at = license_data[
            "expires_at"
        ]

        if expires_at:

            expiration = parse_datetime(
                expires_at
            )

            if not expiration:

                continue

            if utc_now() >= expiration:

                continue

        return True

    return False


# =========================================================
# ACTIVE LICENSE IDS
# =========================================================

def get_active_license_guild_ids():

    licenses = get_all_licenses()

    active_ids = set()

    for guild_id, license_data in licenses.items():

        if license_data["status"] != "active":

            continue

        expires_at = license_data[
            "expires_at"
        ]

        if expires_at:

            expiration = parse_datetime(
                expires_at
            )

            if not expiration:

                continue

            if utc_now() >= expiration:

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
# GET SESSION USER
# =========================================================

def get_session_user():

    access_token = session.get(
        "access_token"
    )

    if not access_token:

        return None

    user_id = session.get(
        "user_id"
    )

    username = session.get(
        "username"
    )

    global_name = session.get(
        "global_name"
    )

    avatar = session.get(
        "avatar"
    )

    if not user_id:

        return None

    return {

        "id":
            user_id,

        "username":
            username,

        "global_name":
            global_name,

        "avatar":
            avatar

    }


# =========================================================
# GET USER
# =========================================================

def get_user():

    session_user = get_session_user()

    if session_user:

        return session_user

    access_token = session.get(
        "access_token"
    )

    if not access_token:

        return None

    try:

        response = discord_http.get(

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

        user = response.json()

    except ValueError:

        return None

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

    session[
        "avatar"
    ] = user.get(
        "avatar"
    )

    session.modified = True

    return user


# =========================================================
# GET USER GUILDS
# =========================================================

def get_user_guilds(access_token=None):

    if access_token is None:

        access_token = session.get(
            "access_token"
        )

    if not access_token:

        return []

    try:

        response = discord_http.get(

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
# BOT GUILD CACHE
# =========================================================

BOT_GUILD_CACHE = {

    "data": [],

    "timestamp": 0

}

BOT_GUILD_CACHE_TTL = 30


# =========================================================
# GET BOT GUILDS
# =========================================================

def get_bot_guilds():

    global BOT_GUILD_CACHE

    if not BOT_TOKEN:

        print(
            "⚠️ Discord bot token is missing."
        )

        return []

    now = time.time()

    if (
        BOT_GUILD_CACHE["data"]
        and
        now - BOT_GUILD_CACHE["timestamp"]
        < BOT_GUILD_CACHE_TTL
    ):

        return BOT_GUILD_CACHE["data"]

    try:

        response = discord_http.get(

            f"{DISCORD_API}/users/@me/guilds",

            headers={
                "Authorization":
                    f"Bot {BOT_TOKEN}"
            },

            timeout=10

        )

    except requests.RequestException as error:

        print(
            f"❌ Discord bot guild request error: {error}"
        )

        return BOT_GUILD_CACHE["data"]

    if response.status_code != 200:

        print(
            f"❌ Discord bot guild request returned "
            f"{response.status_code}"
        )

        return BOT_GUILD_CACHE["data"]

    try:

        data = response.json()

    except ValueError:

        return BOT_GUILD_CACHE["data"]

    if not isinstance(
        data,
        list
    ):

        return BOT_GUILD_CACHE["data"]

    BOT_GUILD_CACHE = {

        "data":
            data,

        "timestamp":
            now

    }

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

    admin_discord_ids = os.getenv(
        "ADMIN_DISCORD_IDS",
        ""
    )

    if not admin_discord_ids:

        return False

    allowed_ids = {

        item.strip()

        for item in admin_discord_ids.split(",")

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

        return False

    stored_state = session.get(
        "oauth_state"
    )

    expires_at_raw = session.get(
        "oauth_state_expires_at"
    )

    if not stored_state:

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

        except ValueError:

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
# VERIFICATION HELPERS
# =========================================================

def get_verification_guild(
    guild_id,
    access_token
):

    try:

        guild_id = str(
            int(guild_id)
        )

    except (
        TypeError,
        ValueError
    ):

        return None

    user_guilds = get_user_guilds(
        access_token
    )

    for guild in user_guilds:

        if str(
            guild.get(
                "id",
                ""
            )
        ) == guild_id:

            return guild

    return None


def bot_is_in_guild(
    guild_id
):

    guild_id = str(
        guild_id
    )

    bot_guilds = get_bot_guilds()

    return any(

        str(
            guild.get(
                "id",
                ""
            )
        ) == guild_id

        for guild in bot_guilds

    )


# =========================================================
# CAPTCHA
# =========================================================

CAPTCHA_TTL = 300

CAPTCHA_MAX_ATTEMPTS = 5


def hash_captcha_answer(answer):

    return hashlib.sha256(
        str(answer)
        .strip()
        .encode("utf-8")
    ).hexdigest()


def generate_captcha():

    first = random.randint(
        2,
        20
    )

    second = random.randint(
        2,
        20
    )

    operation = random.choice(
        [
            "+",
            "-"
        ]
    )

    if operation == "+":

        answer = first + second

    else:

        if second > first:

            first, second = (
                second,
                first
            )

        answer = first - second

    question = (
        f"{first} {operation} {second} = ?"
    )

    return question, answer


def create_captcha(
    guild_id,
    user_id
):

    if not DATABASE_URL or not db_pool:

        return None

    question, answer = generate_captcha()

    token = secrets.token_urlsafe(
        32
    )

    now = time.time()

    expires_at = (
        now + CAPTCHA_TTL
    )

    answer_hash = hash_captcha_answer(
        answer
    )

    try:

        with database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE verification_captchas
                    SET used = TRUE
                    WHERE guild_id = %s
                      AND user_id = %s
                      AND used = FALSE
                    """,
                    (
                        int(guild_id),
                        int(user_id)
                    )
                )

                cursor.execute(
                    """
                    INSERT INTO verification_captchas (
                        token,
                        guild_id,
                        user_id,
                        question,
                        answer_hash,
                        created_at,
                        expires_at,
                        attempts,
                        used
                    )

                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        0,
                        FALSE
                    )
                    """,
                    (
                        token,
                        int(guild_id),
                        int(user_id),
                        question,
                        answer_hash,
                        now,
                        expires_at
                    )
                )

            connection.commit()

        return {
            "token": token,
            "question": question
        }

    except Exception as error:

        print(
            f"❌ CAPTCHA creation error: {error}"
        )

        return None


def validate_captcha(
    token,
    guild_id,
    user_id,
    answer
):

    if not token:

        return False, "invalid"

    if not answer:

        return False, "incorrect"

    if not DATABASE_URL or not db_pool:

        return False, "database"

    try:

        with database_connection() as connection:

            with connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            ) as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        answer_hash,
                        expires_at,
                        attempts,
                        used
                    FROM verification_captchas
                    WHERE token = %s
                      AND guild_id = %s
                      AND user_id = %s
                    LIMIT 1
                    """,
                    (
                        token,
                        int(guild_id),
                        int(user_id)
                    )
                )

                captcha = cursor.fetchone()

                if not captcha:

                    return False, "invalid"

                if captcha["used"]:

                    return False, "expired"

                if time.time() >= float(
                    captcha["expires_at"]
                ):

                    cursor.execute(
                        """
                        UPDATE verification_captchas
                        SET used = TRUE
                        WHERE id = %s
                        """,
                        (
                            captcha["id"],
                        )
                    )

                    connection.commit()

                    return False, "expired"

                attempts = int(
                    captcha["attempts"]
                )

                if attempts >= CAPTCHA_MAX_ATTEMPTS:

                    cursor.execute(
                        """
                        UPDATE verification_captchas
                        SET used = TRUE
                        WHERE id = %s
                        """,
                        (
                            captcha["id"],
                        )
                    )

                    connection.commit()

                    return False, "expired"

                answer_hash = hash_captcha_answer(
                    answer
                )

                if not hmac.compare_digest(
                    answer_hash,
                    captcha["answer_hash"]
                ):

                    attempts += 1

                    used = (
                        attempts >= CAPTCHA_MAX_ATTEMPTS
                    )

                    cursor.execute(
                        """
                        UPDATE verification_captchas
                        SET
                            attempts = %s,
                            used = %s
                        WHERE id = %s
                        """,
                        (
                            attempts,
                            used,
                            captcha["id"]
                        )
                    )

                    connection.commit()

                    if used:

                        return False, "expired"

                    return False, "incorrect"

                cursor.execute(
                    """
                    UPDATE verification_captchas
                    SET used = TRUE
                    WHERE id = %s
                    """,
                    (
                        captcha["id"],
                    )
                )

            connection.commit()

        return True, "valid"

    except Exception as error:

        print(
            f"❌ CAPTCHA validation error: {error}"
        )

        return False, "database"


# =========================================================
# VERIFICATION REQUEST
# =========================================================

def create_verification_request(
    guild_id,
    user_id,
    username
):

    if not DATABASE_URL or not db_pool:

        return False

    try:

        with database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO verification_requests (
                        guild_id,
                        user_id,
                        username,
                        status,
                        created_at,
                        processed_at,
                        failure_reason
                    )

                    VALUES (
                        %s,
                        %s,
                        %s,
                        'pending',
                        %s,
                        NULL,
                        NULL
                    )

                    ON CONFLICT (
                        guild_id,
                        user_id
                    )

                    DO UPDATE SET

                        username =
                            EXCLUDED.username,

                        status =
                            'pending',

                        created_at =
                            EXCLUDED.created_at,

                        processed_at =
                            NULL,

                        failure_reason =
                            NULL
                    """,
                    (
                        int(guild_id),
                        int(user_id),
                        username,
                        time.time()
                    )
                )

            connection.commit()

        return True

    except Exception as error:

        print(
            f"❌ Verification request error: {error}"
        )

        return False


def mark_verification_unverified(
    guild_id,
    user_id,
    username,
    reason
):

    if not DATABASE_URL or not db_pool:

        return False

    try:

        with database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO verification_requests (
                        guild_id,
                        user_id,
                        username,
                        status,
                        created_at,
                        processed_at,
                        failure_reason
                    )

                    VALUES (
                        %s,
                        %s,
                        %s,
                        'unverified',
                        %s,
                        %s,
                        %s
                    )

                    ON CONFLICT (
                        guild_id,
                        user_id
                    )

                    DO UPDATE SET

                        username =
                            EXCLUDED.username,

                        status =
                            'unverified',

                        created_at =
                            EXCLUDED.created_at,

                        processed_at =
                            EXCLUDED.processed_at,

                        failure_reason =
                            EXCLUDED.failure_reason
                    """,
                    (
                        int(guild_id),
                        int(user_id),
                        username,
                        time.time(),
                        time.time(),
                        reason
                    )
                )

            connection.commit()

        return True

    except Exception as error:

        print(
            f"❌ Failed to mark verification unverified: {error}"
        )

        return False


# =========================================================
# STATISTICS
# =========================================================

STATISTICS_OFFLINE_TIMEOUT = 30


def _safe_json_list(value):

    if value is None:

        return []

    if isinstance(value, list):

        return value

    if isinstance(value, tuple):

        return list(value)

    if isinstance(value, str):

        try:

            decoded = json.loads(
                value
            )

            if isinstance(
                decoded,
                list
            ):

                return decoded

        except (
            ValueError,
            TypeError
        ):

            pass

    return []


def get_verified_users_count():

    if not DATABASE_URL or not db_pool:

        return 0

    try:

        with database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM verification_requests
                    WHERE status = 'verified'
                    """
                )

                result = cursor.fetchone()

        if not result:

            return 0

        return int(
            result[0] or 0
        )

    except Exception as error:

        print(
            f"❌ Verification statistics error: {error}"
        )

        return 0


def get_statistics_data(user=None):

    default_statistics = {

        "servers": 0,

        "users": 0,

        "channels": 0,

        "commands": 0,

        "tickets": 0,

        "verifications": 0,

        "bot_status": "Offline",

        "website_status": "Operational",

        "database_status": (
            "Operational"
            if db_pool
            else "Error"
        ),

        "api_status": "Operational",

        "latency": 0,

        "uptime": "0s",

        "version": os.getenv(
            "MISUKI_VERSION",
            "1.0.0"
        ),

        "admin_servers": [],

        "admin_users": [],

        "admin_statistics": {

            "commands": 0,

            "tickets": 0,

            "moderation": 0,

            "announcements": 0

        }

    }

    if not DATABASE_URL or not db_pool:

        return default_statistics

    try:

        with database_connection() as connection:

            with connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            ) as cursor:

                cursor.execute(
                    """
                    SELECT
                        servers,
                        users,
                        channels,
                        latency,
                        commands,
                        verifications,
                        bot_status,
                        uptime,
                        version,
                        last_seen,
                        admin_servers,
                        updated_at
                    FROM bot_statistics
                    WHERE id = 1
                    LIMIT 1
                    """
                )

                row = cursor.fetchone()

    except Exception as error:

        print(
            f"❌ Statistics database error: {error}"
        )

        return default_statistics

    if not row:

        return default_statistics

    try:

        servers = int(
            row.get("servers") or 0
        )

    except (
        TypeError,
        ValueError
    ):

        servers = 0

    try:

        users = int(
            row.get("users") or 0
        )

    except (
        TypeError,
        ValueError
    ):

        users = 0

    try:

        channels = int(
            row.get("channels") or 0
        )

    except (
        TypeError,
        ValueError
    ):

        channels = 0

    try:

        latency = int(
            row.get("latency") or 0
        )

    except (
        TypeError,
        ValueError
    ):

        latency = 0

    try:

        commands = int(
            row.get("commands") or 0
        )

    except (
        TypeError,
        ValueError
    ):

        commands = 0

    # ---------------------------------------------------------
    # VERIFICATIONS
    # ---------------------------------------------------------
    #
    # The verification_requests table is the source of truth
    # for completed verifications. The bot also stores this
    # value in bot_statistics, but reading the database directly
    # here keeps the website accurate if the snapshot is stale.
    # ---------------------------------------------------------

    verifications = get_verified_users_count()

    if verifications == 0:

        try:

            snapshot_verifications = int(
                row.get("verifications") or 0
            )

            if snapshot_verifications > 0:

                verifications = snapshot_verifications

        except (
            TypeError,
            ValueError
        ):

            pass

    # ---------------------------------------------------------
    # BOT STATUS
    # ---------------------------------------------------------

    last_seen = row.get(
        "last_seen"
    )

    bot_status = str(
        row.get(
            "bot_status"
        )
        or
        "Offline"
    )

    try:

        if last_seen is None:

            bot_status = "Offline"

        else:

            seconds_since_heartbeat = (
                time.time()
                -
                float(last_seen)
            )

            if seconds_since_heartbeat > STATISTICS_OFFLINE_TIMEOUT:

                bot_status = "Offline"

            else:

                bot_status = "Online"

    except (
        TypeError,
        ValueError
    ):

        bot_status = "Offline"

    # ---------------------------------------------------------
    # VERSION
    # ---------------------------------------------------------

    version = str(
        row.get(
            "version"
        )
        or
        os.getenv(
            "MISUKI_VERSION",
            "1.0.0"
        )
    )

    # ---------------------------------------------------------
    # UPTIME
    # ---------------------------------------------------------

    uptime = str(
        row.get(
            "uptime"
        )
        or
        "0s"
    )

    # ---------------------------------------------------------
    # ADMIN SERVERS
    # ---------------------------------------------------------

    admin_servers = _safe_json_list(
        row.get(
            "admin_servers"
        )
    )

    cleaned_admin_servers = []

    for guild in admin_servers:

        if not isinstance(
            guild,
            dict
        ):

            continue

        cleaned_admin_servers.append({

            "name":
                str(
                    guild.get(
                        "name",
                        "Unknown Server"
                    )
                ),

            "id":
                str(
                    guild.get(
                        "id",
                        ""
                    )
                ),

            "icon":
                guild.get(
                    "icon"
                ),

            "members":
                int(
                    guild.get(
                        "members",
                        0
                    )
                    or
                    0
                )

        })

    # ---------------------------------------------------------
    # ADMIN USER DATA
    # ---------------------------------------------------------
    #
    # No separate admin-user activity tracker exists yet.
    # Therefore we do not fabricate user statistics.
    # ---------------------------------------------------------

    admin_users = []

    admin_statistics = {

        "commands":
            0,

        "tickets":
            0,

        "moderation":
            0,

        "announcements":
            0

    }

    return {

        "servers":
            servers,

        "users":
            users,

        "channels":
            channels,

        "commands":
            commands,

        "tickets":
            0,

        "verifications":
            verifications,

        "bot_status":
            bot_status,

        "website_status":
            "Operational",

        "database_status":
            "Operational",

        "api_status":
            "Operational",

        "latency":
            latency,

        "uptime":
            uptime,

        "version":
            version,

        "admin_servers":
            cleaned_admin_servers,

        "admin_users":
            admin_users,

        "admin_statistics":
            admin_statistics

    }


# =========================================================
# STATISTICS PAGE
# =========================================================

@app.route(
    "/statistics",
    methods=["GET"]
)
def statistics():

    user = get_user()

    if not user:

        session[
            "next_url"
        ] = "/statistics"

        return redirect(
            "/login"
        )

    statistics_data = get_statistics_data(
        user
    )

    return render_template(
        "statistics.html",
        user=user,
        statistics=statistics_data,
        admin_servers=statistics_data[
            "admin_servers"
        ],
        admin_users=statistics_data[
            "admin_users"
        ],
        admin_statistics=statistics_data[
            "admin_statistics"
        ],
        is_misuki_admin=is_admin(
            user
        )
    )


# =========================================================
# STATISTICS API
# =========================================================

@app.route(
    "/api/statistics",
    methods=["GET"]
)
def statistics_api():

    user = get_user()

    if not user:

        response = jsonify({
            "error":
                "Authentication required"
        })

        response.status_code = 401

        response.headers[
            "Cache-Control"
        ] = "no-store, no-cache, must-revalidate, max-age=0"

        response.headers[
            "Pragma"
        ] = "no-cache"

        return response

    statistics_data = get_statistics_data(
        user
    )

    response = jsonify(
        statistics_data
    )

    response.headers[
        "Cache-Control"
    ] = "no-store, no-cache, must-revalidate, max-age=0"

    response.headers[
        "Pragma"
    ] = "no-cache"

    response.headers[
        "Expires"
    ] = "0"

    return response


# =========================================================
# LEGACY VERIFICATION URL
# =========================================================

@app.route(
    "/verify/guild=<int:guild_id>",
    methods=["GET"]
)
@app.route(
    "/verification/guild=<int:guild_id>",
    methods=["GET"]
)
@app.route(
    "/verify/<int:guild_id>",
    methods=["GET"]
)
@app.route(
    "/verification/<int:guild_id>",
    methods=["GET"]
)
def verification_legacy_url(guild_id):

    return redirect(
        "/verify?"
        + urlencode(
            {
                "guild_id": guild_id
            }
        )
    )


# =========================================================
# DISCORD VERIFICATION
# =========================================================

@app.route(
    "/verify",
    methods=["GET"]
)
@app.route(
    "/verification",
    methods=["GET"]
)
def verification():

    user = get_user()

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    if not user:

        guild_id = request.args.get(
            "guild_id",
            ""
        ).strip()

        if guild_id:

            session[
                "next_url"
            ] = (
                f"/verify?guild_id={guild_id}"
            )

        else:

            session[
                "next_url"
            ] = "/verify"

        return redirect(
            "/login"
        )

    # -----------------------------------------------------
    # GUILD ID
    # -----------------------------------------------------

    guild_id = request.args.get(
        "guild_id",
        ""
    ).strip()

    if not guild_id:

        return error_page(
            "❌ Verification Error",
            "No server was specified for verification.",
            400,
            user
        )

    try:

        guild_id_int = int(
            guild_id
        )

    except (
        TypeError,
        ValueError
    ):

        return error_page(
            "❌ Verification Error",
            "The server ID is invalid.",
            400,
            user
        )

    # -----------------------------------------------------
    # ACCESS TOKEN
    # -----------------------------------------------------

    access_token = session.get(
        "access_token"
    )

    if not access_token:

        session[
            "next_url"
        ] = (
            f"/verify?guild_id={guild_id_int}"
        )

        return redirect(
            "/login"
        )

    # -----------------------------------------------------
    # CHECK USER MEMBERSHIP
    # -----------------------------------------------------

    guild = get_verification_guild(
        guild_id_int,
        access_token
    )

    if guild is None:

        return error_page(
            "❌ Access denied",
            "You are not a member of this Discord server.",
            403,
            user
        )

    # -----------------------------------------------------
    # CHECK BOT
    # -----------------------------------------------------

    if not bot_is_in_guild(
        guild_id_int
    ):

        return error_page(
            "❌ Verification unavailable",
            "The Misuki bot is not installed on this server.",
            400,
            user
        )

    # -----------------------------------------------------
    # CAPTCHA
    # -----------------------------------------------------

    user_id = user.get(
        "id"
    )

    if not user_id:

        return error_page(
            "❌ Verification Error",
            "Your Discord account could not be identified.",
            400,
            user
        )

    captcha = create_captcha(
        guild_id_int,
        user_id
    )

    if not captcha:

        return error_page(
            "❌ Verification Error",
            "The verification challenge could not be created. Please try again.",
            500,
            user
        )

    guild_name = guild.get(
        "name"
    ) or "Discord Server"

    return render_template(
        "verification.html",
        user=user,
        username=(
            user.get("global_name")
            or
            user.get("username")
            or
            "Discord User"
        ),
        guild_name=guild_name,
        guild_id=str(
            guild_id_int
        ),
        captcha_token=captcha["token"],
        captcha_question=captcha["question"],
        captcha_error=None,
        verification_submitted=False
    )


# =========================================================
# SUBMIT VERIFICATION
# =========================================================

@app.route(
    "/verify",
    methods=["POST"]
)
@app.route(
    "/verification",
    methods=["POST"]
)
def submit_verification():

    user = get_user()

    # -----------------------------------------------------
    # LOGIN REQUIRED
    # -----------------------------------------------------

    if not user:

        guild_id = request.form.get(
            "guild_id",
            ""
        ).strip()

        if guild_id:

            session[
                "next_url"
            ] = (
                f"/verify?guild_id={guild_id}"
            )

        else:

            session[
                "next_url"
            ] = "/verify"

        return redirect(
            "/login"
        )

    # -----------------------------------------------------
    # GUILD ID
    # -----------------------------------------------------

    guild_id = request.form.get(
        "guild_id",
        ""
    ).strip()

    if not guild_id:

        return error_page(
            "❌ Verification Error",
            "No server was specified for verification.",
            400,
            user
        )

    try:

        guild_id_int = int(
            guild_id
        )

    except (
        TypeError,
        ValueError
    ):

        return error_page(
            "❌ Verification Error",
            "The server ID is invalid.",
            400,
            user
        )

    # -----------------------------------------------------
    # ACCESS TOKEN
    # -----------------------------------------------------

    access_token = session.get(
        "access_token"
    )

    if not access_token:

        session[
            "next_url"
        ] = (
            f"/verify?guild_id={guild_id_int}"
        )

        return redirect(
            "/login"
        )

    # -----------------------------------------------------
    # CHECK USER MEMBERSHIP
    # -----------------------------------------------------

    guild = get_verification_guild(
        guild_id_int,
        access_token
    )

    if guild is None:

        return error_page(
            "❌ Access denied",
            "You are not a member of this Discord server.",
            403,
            user
        )

    # -----------------------------------------------------
    # CHECK BOT
    # -----------------------------------------------------

    if not bot_is_in_guild(
        guild_id_int
    ):

        return error_page(
            "❌ Verification unavailable",
            "The Misuki bot is not installed on this server.",
            400,
            user
        )

    # -----------------------------------------------------
    # USER INFORMATION
    # -----------------------------------------------------

    user_id = user.get(
        "id"
    )

    if not user_id:

        return error_page(
            "❌ Verification Error",
            "Your Discord account could not be identified.",
            400,
            user
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

    # -----------------------------------------------------
    # CAPTCHA
    # -----------------------------------------------------

    captcha_token = request.form.get(
        "captcha_token",
        ""
    ).strip()

    captcha_answer = request.form.get(
        "captcha_answer",
        ""
    ).strip()

    captcha_valid, captcha_status = validate_captcha(
        captcha_token,
        guild_id_int,
        user_id,
        captcha_answer
    )

    if not captcha_valid:

        if captcha_status == "database":

            return error_page(
                "❌ Verification Error",
                "The CAPTCHA could not be verified. Please try again.",
                500,
                user
            )

        # -------------------------------------------------
        # INTERNAL UNVERIFIED STATE
        # -------------------------------------------------

        mark_verification_unverified(
            guild_id_int,
            user_id,
            username,
            "captcha_failed"
        )

        # -------------------------------------------------
        # CREATE NEW CAPTCHA
        # -------------------------------------------------

        captcha = create_captcha(
            guild_id_int,
            user_id
        )

        if not captcha:

            return error_page(
                "❌ Verification Error",
                "A new CAPTCHA could not be created. Please try again.",
                500,
                user
            )

        if captcha_status == "expired":

            captcha_error = (
                "The CAPTCHA expired or the maximum number "
                "of attempts was reached. A new CAPTCHA has been created."
            )

        else:

            captcha_error = (
                "Incorrect CAPTCHA answer. Please try again."
            )

        return render_template(
            "verification.html",
            user=user,
            username=username,
            guild_name=(
                guild.get("name")
                or
                "Discord Server"
            ),
            guild_id=str(
                guild_id_int
            ),
            captcha_token=captcha["token"],
            captcha_question=captcha["question"],
            captcha_error=captcha_error,
            verification_submitted=False
        )

    # -----------------------------------------------------
    # CREATE REQUEST
    # -----------------------------------------------------

    success = create_verification_request(
        guild_id_int,
        user_id,
        username
    )

    if not success:

        return error_page(
            "❌ Verification Error",
            "The verification request could not be created. Please try again.",
            500,
            user
        )

    print(
        "=========================================="
    )

    print(
        "🔐 VERIFICATION REQUEST CREATED"
    )

    print(
        f"👤 User: {username}"
    )

    print(
        f"🆔 User ID: {user_id}"
    )

    print(
        f"🏠 Guild: {guild.get('name')}"
    )

    print(
        f"🏠 Guild ID: {guild_id_int}"
    )

    print(
        "🧩 CAPTCHA: PASSED"
    )

    print(
        "🤖 Waiting for Misuki bot..."
    )

    print(
        "=========================================="
    )

    return render_template(
        "verification.html",
        user=user,
        username=username,
        guild_name=(
            guild.get("name")
            or
            "Discord Server"
        ),
        guild_id=str(
            guild_id_int
        ),
        verification_submitted=True
    )


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

            or

            session.get(
                "next_url"
            )

        )

        session[
            "next_url"
        ] = next_url

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

        response = discord_http.post(

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

        user_response = discord_http.get(

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

    session[
        "avatar"
    ] = user.get(
        "avatar"
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

    start_time = time.perf_counter()

    print(
        "🟢 DASHBOARD: started"
    )

    user = get_user()

    if not user:

        session[
            "next_url"
        ] = "/dashboard"

        return redirect(
            "/login"
        )

    access_token = session.get(
        "access_token"
    )

    if not access_token:

        session[
            "next_url"
        ] = "/dashboard"

        return redirect(
            "/login"
        )

    with ThreadPoolExecutor(
        max_workers=3
    ) as executor:

        user_guilds_future = executor.submit(
            get_user_guilds,
            access_token
        )

        bot_guilds_future = executor.submit(
            get_bot_guilds
        )

        licenses_future = executor.submit(
            get_all_licenses
        )

        user_guilds = (
            user_guilds_future.result()
        )

        bot_guilds = (
            bot_guilds_future.result()
        )

        licenses = (
            licenses_future.result()
        )

    print(
        f"🏠 DASHBOARD: "
        f"{len(user_guilds)} user guilds"
    )

    print(
        f"🤖 DASHBOARD: "
        f"{len(bot_guilds)} bot guilds"
    )

    print(
        f"🗄️ DASHBOARD: "
        f"{len(licenses)} licenses"
    )

    bot_guild_ids = {

        str(
            guild.get("id")
        )

        for guild in bot_guilds

        if guild.get("id")

    }

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

        license_data = licenses.get(
            guild_id
        )

        guild[
            "license_data"
        ] = license_data

        if license_data:

            status = license_data[
                "status"
            ]

        else:

            status = "none"

        guild[
            "license_status"
        ] = status

        guild[
            "license_active"
        ] = (
            status == "active"
        )

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

    elapsed = (
        time.perf_counter()
        - start_time
    )

    print(
        f"⚡ DASHBOARD: completed "
        f"in {elapsed:.3f}s"
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
# REVIEWS DATABASE
# =========================================================

def get_random_reviews(
    amount=6
):

    if not DATABASE_URL or not db_pool:

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

    if not DATABASE_URL or not db_pool:

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
        f"{bool(os.getenv('ADMIN_DISCORD_IDS'))}"
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