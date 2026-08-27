# =========================================================
# MISUKI OAUTH2
# Dashboard + Discord Login + Bot Installation
# Licenses + Reviews + Likes + Cookies
#
# IMPORTANT:
#
# 1. /login uses OAuth2 ONLY for user authentication.
#
# 2. /install/<guild_id> uses Discord OAuth2 ONLY to
#    install the Misuki bot.
#
# 3. The login Redirect URI is NEVER used by the bot
#    installation URL.
#
# 4. Bot installation does NOT use /login/callback.
# =========================================================

import os
import json
import secrets
import traceback

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from html import escape
from urllib.parse import urlencode

import psycopg2
import requests

from flask import (
    Flask,
    redirect,
    session,
    url_for,
    request
)

from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_DIR = os.path.dirname(
    BASE_DIR
)

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv(
    ENV_FILE
)

CLIENT_ID = os.getenv(
    "DISCORD_CLIENT_ID"
)

CLIENT_SECRET = os.getenv(
    "DISCORD_CLIENT_SECRET"
)

LOGIN_REDIRECT_URI = os.getenv(
    "DISCORD_LOGIN_REDIRECT_URI"
)

FLASK_SECRET_KEY = os.getenv(
    "FLASK_SECRET_KEY"
)

BOT_TOKEN = os.getenv(
    "DISCORD_BOT_TOKEN"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

# ---------------------------------------------------------
# COOKIE SECURITY
#
# Production / HTTPS:
#
# COOKIE_SECURE=true
#
# Local HTTP testing:
#
# COOKIE_SECURE=false
# ---------------------------------------------------------

COOKIE_SECURE = (
    os.getenv(
        "COOKIE_SECURE",
        "true"
    ).lower()
    == "true"
)


# =========================================================
# VALIDATION
# =========================================================

if not FLASK_SECRET_KEY:
    raise RuntimeError(
        "FLASK_SECRET_KEY is not configured."
    )

if not CLIENT_ID:
    raise RuntimeError(
        "DISCORD_CLIENT_ID is not configured."
    )

if not CLIENT_SECRET:
    raise RuntimeError(
        "DISCORD_CLIENT_SECRET is not configured."
    )

if not LOGIN_REDIRECT_URI:
    raise RuntimeError(
        "DISCORD_LOGIN_REDIRECT_URI is not configured."
    )

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured."
    )


# =========================================================
# DISCORD
# =========================================================

DISCORD_API = (
    "https://discord.com/api/v10"
)

BOT_PERMISSIONS = "8"

DISCORD_SUPPORT_SERVER = (
    "https://discord.gg/ppdTV4dasB"
)


# =========================================================
# REVIEW SETTINGS
# =========================================================

REVIEW_LIFETIME_DAYS = 30

HOME_REVIEW_COUNT = 5


# =========================================================
# FLASK
# =========================================================

app = Flask(
    __name__
)

app.secret_key = FLASK_SECRET_KEY

app.config["SESSION_COOKIE_NAME"] = (
    "misuki_session"
)

app.config["SESSION_COOKIE_HTTPONLY"] = True

app.config["SESSION_COOKIE_SECURE"] = (
    COOKIE_SECURE
)

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config["SESSION_COOKIE_PATH"] = "/"

app.config["SESSION_COOKIE_PERMANENT"] = True

app.config["PERMANENT_SESSION_LIFETIME"] = (
    timedelta(days=30)
)


# =========================================================
# PROXY
# =========================================================

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1
)


# =========================================================
# TIME
# =========================================================

def utc_now():
    """
    Returns the current UTC time as a naive datetime.

    Timestamps are stored without timezone information,
    so all internal comparisons use the same UTC-naive
    representation.
    """

    return datetime.now(
        timezone.utc
    ).replace(
        tzinfo=None
    )


# =========================================================
# DATABASE
#
# Postgres (Supabase). Every call opens a short-lived
# connection and always closes it afterwards, since
# free-tier Postgres plans enforce a low connection
# limit.
# =========================================================

@contextmanager
def database():

    connection = psycopg2.connect(
        DATABASE_URL
    )

    try:

        yield connection

    finally:

        connection.close()


# =========================================================
# DATABASE SETUP
# =========================================================

def create_database():

    with database() as connection:

        cursor = connection.cursor()

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
            CREATE TABLE IF NOT EXISTS web_sessions (

                session_id TEXT PRIMARY KEY,

                user_data TEXT NOT NULL,

                guild_data TEXT NOT NULL,

                created_at TEXT NOT NULL,

                expires_at TEXT NOT NULL

            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS installation_states (

                state TEXT PRIMARY KEY,

                guild_id TEXT NOT NULL,

                created_at TEXT NOT NULL,

                expires_at TEXT NOT NULL

            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (

                id SERIAL PRIMARY KEY,

                user_id TEXT NOT NULL,

                username TEXT NOT NULL,

                guild_id TEXT NOT NULL,

                rating INTEGER NOT NULL,

                review TEXT NOT NULL,

                likes INTEGER NOT NULL
                DEFAULT 0,

                created_at TEXT NOT NULL,

                expires_at TEXT

            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS review_likes (

                review_id INTEGER NOT NULL,

                user_id TEXT NOT NULL,

                created_at TEXT NOT NULL,

                PRIMARY KEY (
                    review_id,
                    user_id
                ),

                FOREIGN KEY (
                    review_id
                )
                REFERENCES reviews(id)
                ON DELETE CASCADE

            )
            """
        )

        connection.commit()

        # -------------------------------------------------
        # REVIEWS COLUMN MIGRATION
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT column_name

            FROM information_schema.columns

            WHERE table_name = 'reviews'
            """
        )

        columns = {
            row[0]
            for row in cursor.fetchall()
        }

        migrations = {

            "user_id":
                "ALTER TABLE reviews ADD COLUMN user_id TEXT",

            "username":
                "ALTER TABLE reviews ADD COLUMN username TEXT",

            "guild_id":
                "ALTER TABLE reviews ADD COLUMN guild_id TEXT",

            "rating":
                "ALTER TABLE reviews ADD COLUMN rating INTEGER DEFAULT 5",

            "review":
                "ALTER TABLE reviews ADD COLUMN review TEXT DEFAULT ''",

            "likes":
                "ALTER TABLE reviews ADD COLUMN likes INTEGER DEFAULT 0",

            "created_at":
                "ALTER TABLE reviews ADD COLUMN created_at TEXT",

            "expires_at":
                "ALTER TABLE reviews ADD COLUMN expires_at TEXT"
        }

        for column, sql in migrations.items():

            if column not in columns:

                try:

                    cursor.execute(
                        sql
                    )

                    connection.commit()

                except psycopg2.Error as error:

                    connection.rollback()

                    print(
                        f"Could not add reviews.{column}:",
                        error
                    )

        # -------------------------------------------------
        # REVIEW EXPIRATION MIGRATION
        #
        # Done in Python (not raw SQL) to avoid date-math
        # syntax differences between database engines.
        # -------------------------------------------------

        try:

            cursor.execute(
                """
                SELECT id, created_at

                FROM reviews

                WHERE expires_at IS NULL

                AND created_at IS NOT NULL
                """
            )

            pending = cursor.fetchall()

            for review_id, created_at in pending:

                try:

                    created = datetime.fromisoformat(
                        created_at
                    )

                    expires = (
                        created
                        + timedelta(
                            days=REVIEW_LIFETIME_DAYS
                        )
                    )

                    cursor.execute(
                        """
                        UPDATE reviews

                        SET expires_at = %s

                        WHERE id = %s
                        """,
                        (
                            expires.isoformat(),
                            review_id
                        )
                    )

                except (
                    ValueError,
                    TypeError
                ) as error:

                    print(
                        "Could not migrate review expiration for id",
                        review_id,
                        error
                    )

            connection.commit()

        except psycopg2.Error as error:

            connection.rollback()

            print(
                "Could not migrate review expiration:",
                error
            )

    print(
        "Database ready."
    )


create_database()


# =========================================================
# WEB SESSION
# =========================================================

def create_web_session(
    user,
    guilds
):

    session_id = secrets.token_urlsafe(
        32
    )

    now = utc_now()

    expires = (
        now
        + timedelta(days=30)
    )

    with database() as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO web_sessions
            (
                session_id,
                user_data,
                guild_data,
                created_at,
                expires_at
            )

            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                session_id,

                json.dumps(
                    user,
                    separators=(",", ":")
                ),

                json.dumps(
                    guilds,
                    separators=(",", ":")
                ),

                now.isoformat(),

                expires.isoformat()
            )
        )

        connection.commit()

    return session_id


# =========================================================
# GET WEB SESSION
# =========================================================

def get_web_session(
    session_id
):

    if not session_id:
        return None

    with database() as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                user_data,
                guild_data,
                expires_at

            FROM web_sessions

            WHERE session_id = %s
            """,
            (
                session_id,
            )
        )

        row = cursor.fetchone()

    if not row:
        return None

    try:

        expiration = datetime.fromisoformat(
            row[2]
        )

    except (
        ValueError,
        TypeError
    ):

        delete_web_session(
            session_id
        )

        return None

    if utc_now() >= expiration:

        delete_web_session(
            session_id
        )

        return None

    try:

        return {
            "user":
                json.loads(row[0]),

            "guilds":
                json.loads(row[1])
        }

    except (
        json.JSONDecodeError,
        TypeError
    ):

        delete_web_session(
            session_id
        )

        return None


# =========================================================
# DELETE SESSION
# =========================================================

def delete_web_session(
    session_id
):

    if not session_id:
        return

    with database() as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM web_sessions

            WHERE session_id = %s
            """,
            (
                session_id,
            )
        )

        connection.commit()


# =========================================================
# SESSION CLEANUP
# =========================================================

def cleanup_sessions():

    now = utc_now().isoformat()

    with database() as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM web_sessions

            WHERE expires_at < %s
            """,
            (
                now,
            )
        )

        connection.commit()


# =========================================================
# CURRENT SESSION
# =========================================================

def get_current_web_session():

    cleanup_sessions()

    return get_web_session(
        session.get("sid")
    )


# =========================================================
# DISCORD HEADERS
# =========================================================

def discord_headers(
    token
):

    return {
        "Authorization":
            f"Bearer {token}",

        "Content-Type":
            "application/json"
    }


# =========================================================
# BOT HEADERS
# =========================================================

def bot_headers():

    if not BOT_TOKEN:
        return None

    return {
        "Authorization":
            f"Bot {BOT_TOKEN}",

        "Content-Type":
            "application/json"
    }


# =========================================================
# BOT GUILDS
# =========================================================

def get_bot_guild_ids():

    if not BOT_TOKEN:

        print(
            "DISCORD_BOT_TOKEN not configured."
        )

        return set()

    headers = bot_headers()

    try:

        response = requests.get(

            f"{DISCORD_API}/users/@me/guilds",

            headers=headers,

            timeout=15
        )

    except requests.RequestException as error:

        print(
            "Bot guild request failed:",
            error
        )

        return set()

    if response.status_code != 200:

        print(
            "Bot guild request:",
            response.status_code,
            response.text
        )

        return set()

    try:

        guilds = response.json()

    except ValueError:

        return set()

    return {
        str(guild.get("id"))
        for guild in guilds
        if guild.get("id")
    }


# =========================================================
# USER CAN MANAGE GUILD
# =========================================================

def user_can_manage_guild(
    guild
):

    permissions = guild.get(
        "permissions"
    )

    if permissions is None:
        return False

    try:

        permissions = int(
            permissions
        )

    except (
        TypeError,
        ValueError
    ):

        return False

    ADMINISTRATOR = 1 << 3

    MANAGE_GUILD = 1 << 5

    return bool(
        permissions
        & (
            ADMINISTRATOR
            | MANAGE_GUILD
        )
    )


# =========================================================
# FIND USER GUILD
# =========================================================

def get_user_guild(
    current,
    guild_id
):

    if current is None:
        return None

    target = str(
        guild_id
    )

    for guild in current.get(
        "guilds",
        []
    ):

        if str(
            guild.get("id")
        ) == target:

            return guild

    return None


# =========================================================
# LICENSE
# =========================================================

def get_license(
    guild_id
):

    try:

        guild_id = int(
            guild_id
        )

    except (
        TypeError,
        ValueError
    ):

        return None

    with database() as connection:

        cursor = connection.cursor()

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
            """,
            (
                guild_id,
            )
        )

        return cursor.fetchone()


# =========================================================
# EXPIRE LICENSE
# =========================================================

def set_license_expired(
    guild_id
):

    try:

        guild_id = int(
            guild_id
        )

    except (
        TypeError,
        ValueError
    ):

        return

    with database() as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE licenses

            SET status = 'expired'

            WHERE guild_id = %s
            """,
            (
                guild_id,
            )
        )

        connection.commit()


# =========================================================
# LICENSE STATUS
# =========================================================

def license_status(
    guild_id
):

    data = get_license(
        guild_id
    )

    if data is None:

        return {
            "licensed": False,
            "status": "none",
            "expires_at": None
        }

    status = data[2]

    expires_at = data[3]

    if status == "active" and expires_at:

        try:

            expiration = datetime.fromisoformat(
                expires_at
            )

            if utc_now() >= expiration:

                set_license_expired(
                    guild_id
                )

                status = "expired"

        except (
            ValueError,
            TypeError
        ):

            status = "invalid"

    return {
        "licensed":
            status == "active",

        "status":
            status,

        "expires_at":
            expires_at
    }


# =========================================================
# DISCORD LOGIN URL
#
# THIS OAuth2 FLOW IS ONLY FOR LOGIN.
# =========================================================

def discord_login_url(
    state
):

    params = {

        "client_id":
            CLIENT_ID,

        "response_type":
            "code",

        "redirect_uri":
            LOGIN_REDIRECT_URI,

        "scope":
            "identify guilds",

        "state":
            state
    }

    return (
        "https://discord.com/oauth2/authorize?"
        + urlencode(params)
    )


# =========================================================
# LOGIN
#
# OAuth2 ONLY FOR WEBSITE LOGIN.
#
# Reuses a pending "login_state" instead of always
# generating a new one, so double clicks / parallel
# tabs / slow cold-starts don't invalidate a request
# that is already in flight with Discord.
# =========================================================

@app.route(
    "/login"
)
def login():

    current = get_current_web_session()

    if current is not None:

        return redirect(
            url_for(
                "dashboard"
            )
        )

    existing_state = session.get(
        "login_state"
    )

    if existing_state:

        return redirect(
            discord_login_url(
                existing_state
            )
        )

    state = secrets.token_urlsafe(
        32
    )

    session["login_state"] = state

    session.permanent = True

    return redirect(
        discord_login_url(
            state
        )
    )


# =========================================================
# LOGIN CALLBACK
#
# ONLY FOR USER LOGIN.
#
# NEVER USED BY BOT INSTALLATION.
# =========================================================

@app.route(
    "/login/callback"
)
def login_callback():

    expected_state = session.pop(
        "login_state",
        None
    )

    received_state = request.args.get(
        "state"
    )

    if not expected_state:

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Login Session Expired
                </h1>

                <p>
                    Please try logging in again.
                </p>

                <a
                    class="button"
                    href="/login"
                >
                    🎮 Login with Discord
                </a>

            </div>
            """
        ), 400

    if not received_state:

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Invalid Login
                </h1>

                <p>
                    Discord did not return a login state.
                </p>

            </div>
            """
        ), 400

    if not secrets.compare_digest(
        expected_state,
        received_state
    ):

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Invalid Login State
                </h1>

                <p>
                    The Discord login could not be
                    verified.
                </p>

                <a
                    class="button"
                    href="/login"
                >
                    Try Again
                </a>

            </div>
            """
        ), 400

    error = request.args.get(
        "error"
    )

    if error:

        return page(
            "Login Cancelled",
            """
            <div class="card center">

                <h1>
                    ❌ Login Cancelled
                </h1>

                <p>
                    Discord did not complete the login.
                </p>

                <a
                    class="button"
                    href="/"
                >
                    Return Home
                </a>

            </div>
            """
        ), 400

    code = request.args.get(
        "code"
    )

    if not code:

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Login Failed
                </h1>

                <p>
                    Discord did not provide an
                    authorization code.
                </p>

            </div>
            """
        ), 400

    # =====================================================
    # EXCHANGE LOGIN CODE
    # =====================================================

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
            LOGIN_REDIRECT_URI
    }

    try:

        response = requests.post(

            f"{DISCORD_API}/oauth2/token",

            data=token_data,

            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded"
            },

            timeout=15
        )

    except requests.RequestException as error:

        print(
            "Discord login token request failed:",
            error
        )

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Discord Connection Error
                </h1>

                <p>
                    Could not connect to Discord.
                </p>

                <a
                    class="button"
                    href="/"
                >
                    Return Home
                </a>

            </div>
            """
        ), 500

    if response.status_code != 200:

        print(
            "Discord login token response:",
            response.status_code,
            response.text
        )

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Discord Login Rejected
                </h1>

                <p>
                    Discord rejected the login request.
                </p>

                <a
                    class="button"
                    href="/login"
                >
                    Try Again
                </a>

            </div>
            """
        ), 400

    try:

        token_json = response.json()

    except ValueError:

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Invalid Discord Response
                </h1>

            </div>
            """
        ), 400

    access_token = token_json.get(
        "access_token"
    )

    if not access_token:

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Access Token Missing
                </h1>

            </div>
            """
        ), 400

    # =====================================================
    # GET DISCORD USER
    # =====================================================

    try:

        user_response = requests.get(

            f"{DISCORD_API}/users/@me",

            headers=discord_headers(
                access_token
            ),

            timeout=15
        )

        guild_response = requests.get(

            f"{DISCORD_API}/users/@me/guilds",

            headers=discord_headers(
                access_token
            ),

            timeout=15
        )

    except requests.RequestException as error:

        print(
            "Discord account request failed:",
            error
        )

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Discord Connection Error
                </h1>

                <p>
                    Could not load your Discord account.
                </p>

            </div>
            """
        ), 500

    if user_response.status_code != 200:

        print(
            "User request:",
            user_response.status_code,
            user_response.text
        )

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Could Not Load Discord Account
                </h1>

            </div>
            """
        ), 400

    if guild_response.status_code != 200:

        print(
            "Guild request:",
            guild_response.status_code,
            guild_response.text
        )

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Could Not Load Discord Servers
                </h1>

            </div>
            """
        ), 400

    try:

        user = user_response.json()

        guilds = guild_response.json()

    except ValueError:

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Invalid Discord Data
                </h1>

            </div>
            """
        ), 400

    # =====================================================
    # CREATE WEB SESSION
    # =====================================================

    old_session_id = session.get(
        "sid"
    )

    if old_session_id:

        delete_web_session(
            old_session_id
        )

    session_id = create_web_session(
        user,
        guilds
    )

    session.clear()

    session["sid"] = session_id

    session.permanent = True

    return redirect(
        url_for(
            "dashboard"
        )
    )


# =========================================================
# BOT INSTALL URL
#
# THIS OAuth2 FLOW IS ONLY FOR INSTALLING THE BOT.
#
# IMPORTANT:
#
# There is NO:
#
#     response_type=code
#
# There is NO:
#
#     redirect_uri
#
# There is NO:
#
#     /login/callback
# =========================================================

def bot_install_url(
    guild_id
):

    params = {

        "client_id":
            CLIENT_ID,

        "scope":
            "bot applications.commands",

        "permissions":
            BOT_PERMISSIONS,

        "guild_id":
            str(guild_id),

        "disable_guild_select":
            "true"
    }

    return (
        "https://discord.com/oauth2/authorize?"
        + urlencode(params)
    )


# =========================================================
# INSTALL BOT
# =========================================================

@app.route(
    "/install/<guild_id>"
)
def install_bot(
    guild_id
):

    current = get_current_web_session()

    if current is None:

        return redirect(
            url_for(
                "login"
            )
        )

    # -----------------------------------------------------
    # VALIDATE SERVER ID
    # -----------------------------------------------------

    try:

        guild_id = str(
            int(guild_id)
        )

    except (
        TypeError,
        ValueError
    ):

        return page(
            "Invalid Server",
            """
            <div class="card center">

                <h1>
                    ❌ Invalid Server
                </h1>

                <p>
                    The Discord server ID is invalid.
                </p>

                <a
                    class="button"
                    href="/dashboard"
                >
                    Back to Dashboard
                </a>

            </div>
            """
        ), 400

    # -----------------------------------------------------
    # FIND SERVER
    # -----------------------------------------------------

    guild = get_user_guild(
        current,
        guild_id
    )

    if guild is None:

        return page(
            "Access Denied",
            """
            <div class="card center">

                <h1>
                    🔒 Access Denied
                </h1>

                <p>
                    This server is not available
                    to your Discord account.
                </p>

                <a
                    class="button"
                    href="/dashboard"
                >
                    Back to Dashboard
                </a>

            </div>
            """
        ), 403

    # -----------------------------------------------------
    # PERMISSION CHECK
    #
    # This is the authoritative check. The dashboard only
    # hides/disables the "Add Misuki" button as a UX hint;
    # this server-side check is what actually blocks
    # unauthorized installs.
    # -----------------------------------------------------

    if not user_can_manage_guild(
        guild
    ):

        return page(
            "Permission Required",
            """
            <div class="card center">

                <h1>
                    🔒 Permission Required
                </h1>

                <p>
                    You need Manage Server or
                    Administrator permission to
                    install Misuki.
                </p>

                <a
                    class="button"
                    href="/dashboard"
                >
                    Back to Dashboard
                </a>

            </div>
            """
        ), 403

    # -----------------------------------------------------
    # ALREADY INSTALLED?
    # -----------------------------------------------------

    bot_guild_ids = get_bot_guild_ids()

    if guild_id in bot_guild_ids:

        return redirect(
            url_for(
                "manage",
                guild_id=guild_id
            )
        )

    # -----------------------------------------------------
    # OPEN DISCORD INSTALLATION
    # -----------------------------------------------------

    invite = bot_install_url(
        guild_id
    )

    return redirect(
        invite
    )


# =========================================================
# REVIEWS
# =========================================================

def cleanup_reviews():

    now = utc_now().isoformat()

    with database() as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM reviews

            WHERE expires_at IS NOT NULL

            AND expires_at < %s
            """,
            (
                now,
            )
        )

        connection.commit()


def get_reviews(
    limit=5
):

    cleanup_reviews()

    try:

        limit = int(
            limit
        )

    except (
        TypeError,
        ValueError
    ):

        limit = 5

    limit = max(
        1,
        min(
            limit,
            50
        )
    )

    with database() as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                user_id,
                username,
                guild_id,
                rating,
                review,
                likes,
                created_at,
                expires_at

            FROM reviews

            ORDER BY RANDOM()

            LIMIT %s
            """,
            (
                limit,
            )
        )

        return cursor.fetchall()


def can_user_review(
    user_id
):

    session_data = get_current_web_session()

    if session_data is None:
        return False

    guilds = session_data.get(
        "guilds",
        []
    )

    for guild in guilds:

        guild_id = guild.get(
            "id"
        )

        if not guild_id:
            continue

        if not user_can_manage_guild(
            guild
        ):
            continue

        license_info = license_status(
            guild_id
        )

        if license_info["licensed"]:

            return True

    return False


def add_review(
    user_id,
    username,
    guild_id,
    rating,
    review_text
):

    now = utc_now()

    expires = (
        now
        + timedelta(
            days=REVIEW_LIFETIME_DAYS
        )
    )

    with database() as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO reviews
            (
                user_id,
                username,
                guild_id,
                rating,
                review,
                likes,
                created_at,
                expires_at
            )

            VALUES (%s, %s, %s, %s, %s, 0, %s, %s)
            """,
            (
                str(user_id),
                username,
                str(guild_id),
                int(rating),
                review_text,
                now.isoformat(),
                expires.isoformat()
            )
        )

        connection.commit()


# =========================================================
# LIKE
# =========================================================

def toggle_like(
    review_id,
    user_id
):

    with database() as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT 1

            FROM reviews

            WHERE id = %s
            """,
            (
                review_id,
            )
        )

        if cursor.fetchone() is None:

            return False

        cursor.execute(
            """
            SELECT 1

            FROM review_likes

            WHERE review_id = %s

            AND user_id = %s
            """,
            (
                review_id,
                str(user_id)
            )
        )

        existing = cursor.fetchone()

        if existing:

            cursor.execute(
                """
                DELETE FROM review_likes

                WHERE review_id = %s

                AND user_id = %s
                """,
                (
                    review_id,
                    str(user_id)
                )
            )

            cursor.execute(
                """
                UPDATE reviews

                SET likes = GREATEST(likes - 1, 0)

                WHERE id = %s
                """,
                (
                    review_id,
                )
            )

            connection.commit()

            return False

        cursor.execute(
            """
            INSERT INTO review_likes
            (
                review_id,
                user_id,
                created_at
            )

            VALUES (%s, %s, %s)
            """,
            (
                review_id,
                str(user_id),
                utc_now().isoformat()
            )
        )

        cursor.execute(
            """
            UPDATE reviews

            SET likes = likes + 1

            WHERE id = %s
            """,
            (
                review_id,
            )
        )

        connection.commit()

        return True


# =========================================================
# PAGE
# =========================================================

def page(
    title,
    content
):

    current = get_current_web_session()

    logged_in = current is not None

    if logged_in:

        auth_button = """
        <a href="/dashboard">
            Dashboard
        </a>

        <a href="/logout">
            Log Out
        </a>
        """

    else:

        auth_button = """
        <a href="/login">
            🎮 Login with Discord
        </a>
        """

    return f"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
    {escape(title)} — Misuki
</title>

<style>

* {{
    box-sizing: border-box;
}}

html {{
    scroll-behavior: smooth;
}}

body {{

    margin: 0;

    min-height: 100vh;

    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Arial,
        sans-serif;

    color: #ffffff;

    background:
        radial-gradient(
            circle at 10% 0%,
            #303653 0%,
            #161923 38%,
            #090a0f 100%
        );
}}

a {{
    color: inherit;
}}

.navbar {{

    height: 72px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 0 32px;

    position: sticky;

    top: 0;

    z-index: 100;

    background:
        rgba(10,11,16,0.82);

    border-bottom:
        1px solid
        rgba(255,255,255,0.08);

    backdrop-filter:
        blur(20px);
}}

.brand {{

    color: white;

    text-decoration: none;

    font-size: 21px;

    font-weight: 800;
}}

.hamburger {{

    width: 44px;

    height: 44px;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 12px;

    border:
        1px solid
        rgba(255,255,255,0.08);

    background:
        #1d2028;

    color: white;

    cursor: pointer;

    font-size: 22px;
}}

.hamburger:hover {{
    background: #303440;
}}

.menu {{

    position: absolute;

    right: 24px;

    top: 62px;

    min-width: 210px;

    padding: 10px;

    display: none;

    flex-direction: column;

    gap: 4px;

    border-radius: 15px;

    background:
        #1b1e27;

    border:
        1px solid
        rgba(255,255,255,0.09);

    box-shadow:
        0 20px 60px
        rgba(0,0,0,0.45);
}}

.menu.show {{
    display: flex;
}}

.menu a {{

    padding: 11px 13px;

    border-radius: 9px;

    color: #bfc4d2;

    text-decoration: none;

    font-size: 14px;
}}

.menu a:hover {{

    color: white;

    background:
        #252934;
}}

.container {{

    width: 100%;

    max-width: 1100px;

    margin: 0 auto;

    padding: 50px 22px;
}}

.card {{

    padding: 30px;

    margin-bottom: 20px;

    background:
        rgba(27,30,39,0.91);

    border:
        1px solid
        rgba(255,255,255,0.08);

    border-radius: 22px;

    box-shadow:
        0 25px 80px
        rgba(0,0,0,0.28);
}}

.center {{
    text-align: center;
}}

.logo {{

    width: 88px;

    height: 88px;

    margin:
        0 auto 24px;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 26px;

    font-size: 42px;

    background:
        linear-gradient(
            135deg,
            #5865f2,
            #8b5cf6
        );

    box-shadow:
        0 18px 50px
        rgba(88,101,242,0.35);
}}

h1 {{

    margin:
        0 0 14px;

    font-size:
        clamp(32px, 5vw, 48px);
}}

h2 {{
    margin-top: 0;
}}

p {{

    color: #aeb3c0;

    line-height: 1.75;
}}

.button {{

    display: inline-block;

    margin-top: 18px;

    padding:
        13px 20px;

    border-radius: 12px;

    background: #5865f2;

    color: white;

    text-decoration: none;

    font-weight: 700;

    border:
        1px solid
        rgba(255,255,255,0.08);

    transition:
        transform .2s,
        background .2s;
}}

.button:hover {{

    transform:
        translateY(-2px);

    background:
        #4752c4;
}}

.button.disabled {{

    background: #2b2e37;

    color: #6c7181;

    cursor: not-allowed;

    pointer-events: none;

    border-color:
        rgba(255,255,255,0.05);
}}

.button.disabled:hover {{

    transform: none;

    background: #2b2e37;
}}

.secondary {{
    background: #252934;
}}

.secondary:hover {{
    background: #303440;
}}

.green {{
    background: #248046;
}}

.green:hover {{
    background: #1d6c3b;
}}

.red {{
    background: #ed4245;
}}

.server-grid {{

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(280px, 1fr)
        );

    gap: 18px;

    margin-top: 25px;
}}

.server {{

    padding: 22px;

    background:
        linear-gradient(
            145deg,
            #252933,
            #1e2129
        );

    border:
        1px solid
        rgba(255,255,255,0.07);

    border-radius: 18px;

    transition:
        transform .2s,
        border-color .2s;
}}

.server:hover {{

    transform:
        translateY(-3px);

    border-color:
        rgba(88,101,242,0.4);
}}

.server-header {{

    display: flex;

    align-items: center;

    gap: 14px;

    margin-bottom: 15px;
}}

.server-icon {{

    width: 48px;

    height: 48px;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 15px;

    background:
        #5865f2;

    font-size: 22px;

    font-weight: 800;

    overflow: hidden;

    flex-shrink: 0;
}}

.server-icon img {{

    width: 100%;

    height: 100%;

    object-fit: cover;
}}

.server-name {{

    font-size: 17px;

    font-weight: 750;
}}

.server-id {{

    margin-top: 4px;

    color: #777d8c;

    font-size: 11px;

    word-break: break-all;
}}

.badge {{

    display: inline-block;

    margin-top: 12px;

    margin-right: 5px;

    padding:
        6px 10px;

    border-radius: 8px;

    font-size: 11px;

    font-weight: 700;
}}

.badge-green {{

    background:
        rgba(87,242,135,0.12);

    color:
        #57f287;
}}

.badge-red {{

    background:
        rgba(237,66,69,0.12);

    color:
        #ed4245;
}}

.badge-yellow {{

    background:
        rgba(254,231,92,0.12);

    color:
        #fee75c;
}}

.badge-gray {{

    background:
        rgba(148,155,171,0.12);

    color:
        #949bab;
}}

.actions {{

    display: flex;

    gap: 9px;

    flex-wrap: wrap;

    margin-top: 16px;
}}

.actions .button {{

    margin-top: 0;

    font-size: 13px;

    padding:
        10px 14px;
}}

.profile {{

    display: flex;

    align-items: center;

    gap: 18px;
}}

.avatar {{

    width: 64px;

    height: 64px;

    border-radius: 50%;

    object-fit: cover;
}}

.notice {{

    padding: 17px 19px;

    margin-bottom: 20px;

    border-radius: 14px;

    background:
        rgba(88,101,242,0.10);

    border:
        1px solid
        rgba(88,101,242,0.20);

    color: #bfc4d2;

    line-height: 1.6;
}}

.review-grid {{

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(260px, 1fr)
        );

    gap: 18px;

    margin-top: 25px;
}}

.review {{

    padding: 22px;

    border-radius: 18px;

    background:
        linear-gradient(
            145deg,
            #252933,
            #1d2028
        );

    border:
        1px solid
        rgba(255,255,255,0.07);
}}

.review-header {{

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 10px;
}}

.review-user {{

    font-weight: 750;

    color: white;
}}

.stars {{

    color: #fee75c;

    font-size: 15px;

    letter-spacing: 1px;
}}

.review-text {{

    margin-top: 15px;

    color: #b8bdc9;

    line-height: 1.7;

    white-space: pre-wrap;

    word-break: break-word;
}}

.review-footer {{

    display: flex;

    align-items: center;

    justify-content: space-between;

    margin-top: 18px;

    color: #777d8c;

    font-size: 12px;
}}

.like-button {{

    display: inline-block;

    padding:
        7px 11px;

    border-radius: 9px;

    background:
        #252934;

    color: #bfc4d2;

    text-decoration: none;

    border:
        1px solid
        rgba(255,255,255,0.07);
}}

.like-button:hover {{

    background:
        #303440;

    color: white;
}}

.form-input {{

    width: 100%;

    margin-top: 8px;

    margin-bottom: 18px;

    padding: 12px 14px;

    border-radius: 11px;

    border:
        1px solid
        rgba(255,255,255,0.10);

    background:
        #171a21;

    color: white;

    font-family: inherit;
}}

textarea.form-input {{

    min-height: 130px;

    resize: vertical;
}}

select.form-input {{
    cursor: pointer;
}}

.legal h1 {{
    font-size: 40px;
}}

.legal h2 {{

    margin-top: 34px;

    font-size: 21px;
}}

.legal p,
.legal li {{

    color: #aeb3c0;

    line-height: 1.85;
}}

.legal ul {{
    padding-left: 22px;
}}

.cookie-banner {{

    position: fixed;

    left: 20px;

    right: 20px;

    bottom: 20px;

    z-index: 1000;

    max-width: 1000px;

    margin: auto;

    padding: 20px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 20px;

    background:
        rgba(25,28,36,0.97);

    border:
        1px solid
        rgba(255,255,255,0.10);

    border-radius: 18px;

    box-shadow:
        0 20px 70px
        rgba(0,0,0,0.45);

    backdrop-filter:
        blur(20px);
}}

.cookie-text {{

    color: #aeb3c0;

    font-size: 13px;

    line-height: 1.6;
}}

.cookie-text a {{

    color: #8ea0ff;

    text-decoration: none;
}}

.cookie-actions {{

    display: flex;

    gap: 8px;

    flex-wrap: wrap;

    flex-shrink: 0;
}}

.cookie-actions button {{

    padding:
        10px 14px;

    border-radius: 10px;

    border:
        1px solid
        rgba(255,255,255,0.08);

    background:
        #252934;

    color: white;

    cursor: pointer;

    font-weight: 700;
}}

.cookie-actions button:hover {{
    background: #303440;
}}

footer {{

    margin-top: 45px;

    padding:
        25px 0 40px;

    text-align: center;

    color: #686d7a;

    font-size: 13px;
}}

footer a {{

    margin:
        0 8px;

    color: #858a98;

    text-decoration: none;
}}

footer a:hover {{
    color: white;
}}

.contact-link {{

    display: inline-block;

    margin-top: 10px;

    color: #8ea0ff;

    text-decoration: none;
}}

@media (max-width: 700px) {{

    .navbar {{
        padding: 0 16px;
    }}

    .container {{
        padding:
            30px 15px;
    }}

    .card {{
        padding: 22px;
    }}

    .profile {{
        align-items: flex-start;
    }}

    .cookie-banner {{

        left: 10px;

        right: 10px;

        bottom: 10px;

        flex-direction: column;

        align-items: stretch;
    }}

    .cookie-actions {{
        width: 100%;
    }}

    .cookie-actions button {{
        flex: 1;
    }}

}}

</style>

</head>

<body>

<nav class="navbar">

    <a
        class="brand"
        href="/"
    >
        🌸 Misuki
    </a>

    <div style="position:relative;">

        <button
            class="hamburger"
            onclick="toggleMenu()"
            aria-label="Open menu"
        >
            ☰
        </button>

        <div
            id="menu"
            class="menu"
        >

            <a href="/">
                Home
            </a>

            {auth_button}

            <a href="/review">
                Reviews
            </a>

            <a href="/cookies">
                Cookies
            </a>

        </div>

    </div>

</nav>

<main class="container">

{content}

</main>

<footer>

    © 2026 Misuki

    <br><br>

    <a href="/cookies">
        Cookies
    </a>

    <a href="/cookies#terms">
        Terms
    </a>

    <a href="/cookies#privacy">
        Privacy
    </a>

    <br>

    <a
        class="contact-link"
        href="{DISCORD_SUPPORT_SERVER}"
        target="_blank"
        rel="noopener noreferrer"
    >
        💬 Join our Discord
    </a>

</footer>

<script>

function toggleMenu() {{

    const menu =
        document.getElementById("menu");

    menu.classList.toggle("show");
}}

document.addEventListener(
    "click",
    function(event) {{

        const menu =
            document.getElementById("menu");

        const button =
            document.querySelector(".hamburger");

        if (
            !menu.contains(event.target)
            &&
            !button.contains(event.target)
        ) {{

            menu.classList.remove("show");
        }}
    }}
);

</script>

</body>

</html>
"""


# =========================================================
# COOKIE BANNER
# =========================================================

COOKIE_BANNER = """
<div
    id="cookieBanner"
    class="cookie-banner"
>

    <div class="cookie-text">

        🍪 We use essential cookies to keep you
        signed in and maintain your session.

        <br>

        Read our
        <a href="/cookies">
            Cookie Policy
        </a>,
        <a href="/cookies#terms">
            Terms
        </a>
        and
        <a href="/cookies#privacy">
            Privacy Policy
        </a>.

    </div>

    <div class="cookie-actions">

        <button
            onclick="acceptAllCookies()"
        >
            Accept All
        </button>

        <button
            onclick="acceptNecessaryCookies()"
        >
            Necessary Only
        </button>

        <button
            onclick="rejectCookies()"
        >
            Reject
        </button>

    </div>

</div>

<script>

function setCookieChoice(choice) {{

    localStorage.setItem(
        "misuki_cookie_choice",
        choice
    );

    const banner =
        document.getElementById(
            "cookieBanner"
        );

    if (banner) {{
        banner.remove();
    }}
}}

function acceptAllCookies() {{

    setCookieChoice(
        "all"
    );
}}

function acceptNecessaryCookies() {{

    setCookieChoice(
        "necessary"
    );
}}

function rejectCookies() {{

    setCookieChoice(
        "necessary"
    );
}}

document.addEventListener(
    "DOMContentLoaded",
    function() {{

        const choice =
            localStorage.getItem(
                "misuki_cookie_choice"
            );

        if (choice) {{

            const banner =
                document.getElementById(
                    "cookieBanner"
                );

            if (banner) {{
                banner.remove();
            }}
        }}
    }}
);

</script>
"""


# =========================================================
# RENDER REVIEWS
# =========================================================

def render_reviews(
    reviews
):

    if not reviews:

        return """
        <div class="notice">
            No reviews available yet.
        </div>
        """

    html = ""

    for review in reviews:

        (
            review_id,
            user_id,
            username,
            guild_id,
            rating,
            text,
            likes,
            created_at,
            expires_at
        ) = review

        try:

            rating = int(
                rating
            )

        except (
            TypeError,
            ValueError
        ):

            rating = 1

        rating = max(
            1,
            min(
                5,
                rating
            )
        )

        try:

            likes = max(
                0,
                int(likes)
            )

        except (
            TypeError,
            ValueError
        ):

            likes = 0

        stars = (
            "★" * rating
            +
            "☆" * (5 - rating)
        )

        safe_username = escape(
            username or "Discord User"
        )

        safe_text = escape(
            text or ""
        )

        date_text = ""

        try:

            date = datetime.fromisoformat(
                created_at
            )

            date_text = date.strftime(
                "%d/%m/%Y"
            )

        except (
            ValueError,
            TypeError
        ):

            pass

        html += f"""

        <div class="review">

            <div class="review-header">

                <div class="review-user">
                    {safe_username}
                </div>

                <div class="stars">
                    {stars}
                </div>

            </div>

            <div class="review-text">
                "{safe_text}"
            </div>

            <div class="review-footer">

                <span>
                    {date_text}
                </span>

                <form
                    method="POST"
                    action="/like/{int(review_id)}"
                    style="margin:0;"
                >

                    <button
                        class="like-button"
                        type="submit"
                    >
                        👍 {likes}
                    </button>

                </form>

            </div>

        </div>

        """

    return html


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    reviews = get_reviews(
        HOME_REVIEW_COUNT
    )

    review_html = render_reviews(
        reviews
    )

    content = f"""
    <div class="card center">

        <div class="logo">
            🌸
        </div>

        <h1>
            Welcome to Misuki
        </h1>

        <p>
            A powerful Discord bot designed to make
            your server easier to manage.
        </p>

        <div class="actions" style="justify-content:center;">

            <a
                class="button"
                href="/dashboard"
            >
                🚀 Open Dashboard
            </a>

            <a
                class="button secondary"
                href="/review"
            >
                ⭐ Reviews
            </a>

        </div>

    </div>

    <div class="card">

        <h2>
            ⭐ What people say
        </h2>

        <div class="review-grid">
            {review_html}
        </div>

    </div>
    """

    return page(
        "Home",
        content
        + COOKIE_BANNER
    )


# =========================================================
# DASHBOARD
#
# Layout rules:
#
# - AVAILABLE SERVERS are listed FIRST.
#   Shows every server the user belongs to where Misuki
#   is NOT installed. "Add Misuki" is only clickable if
#   the user has Manage Server / Administrator permission
#   there; otherwise a disabled "Missing Permissions"
#   indicator is shown instead (the /install route is the
#   real, authoritative permission check).
#
# - AUTHORIZED SERVERS are listed SECOND.
#   Shows every server the user belongs to where Misuki
#   IS installed, regardless of the user's permission
#   level, with a badge for install status and license
#   status. "Manage" is only clickable if the user has
#   permission; otherwise a "No Permission" badge is shown
#   (the /manage route is the real, authoritative
#   permission check). The license expiration date is
#   shown directly on the card, and "Manage" leads to
#   full license details.
# =========================================================

@app.route("/dashboard")
def dashboard():

    current = get_current_web_session()

    if current is None:

        return redirect(
            url_for(
                "login"
            )
        )

    user = current.get(
        "user",
        {}
    )

    guilds = current.get(
        "guilds",
        []
    )

    # -----------------------------------------------------
    # GET SERVERS WHERE MISUKI IS ALREADY INSTALLED
    # -----------------------------------------------------

    bot_guild_ids = get_bot_guild_ids()

    authorized = []
    available = []

    # -----------------------------------------------------
    # CLASSIFY SERVERS
    #
    # AUTHORIZED:
    #   Misuki is already installed
    #   (shown even if the user cannot manage it)
    #
    # AVAILABLE:
    #   Misuki is NOT installed
    #   (shown even if the user cannot manage it, but
    #   the "Add" action is blocked without permission)
    # -----------------------------------------------------

    for guild in guilds:

        guild_id = guild.get(
            "id"
        )

        if not guild_id:
            continue

        guild_id = str(
            guild_id
        )

        if guild_id in bot_guild_ids:

            authorized.append(
                guild
            )

        else:

            available.append(
                guild
            )

    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------

    username = escape(
        user.get(
            "global_name"
        )
        or user.get(
            "username"
        )
        or "Discord User"
    )

    avatar = user.get(
        "avatar"
    )

    user_id = user.get(
        "id"
    )

    avatar_url = None

    if avatar and user_id:

        avatar_url = (
            "https://cdn.discordapp.com/"
            f"avatars/{user_id}/{avatar}.png"
        )

    if avatar_url:

        profile_html = f"""
        <img
            class="avatar"
            src="{escape(avatar_url)}"
            alt="Discord avatar"
        >
        """

    else:

        profile_html = """
        <div
            class="avatar"
            style="
                background:#5865f2;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:25px;
            "
        >
            👤
        </div>
        """

    # -----------------------------------------------------
    # SERVER ICON
    # -----------------------------------------------------

    def guild_icon(guild):

        guild_id = guild.get(
            "id"
        )

        icon = guild.get(
            "icon"
        )

        if icon and guild_id:

            icon_url = (
                "https://cdn.discordapp.com/"
                f"icons/{guild_id}/{icon}.png"
            )

            return f"""
            <img
                src="{escape(icon_url)}"
                alt="Server icon"
            >
            """

        name = (
            guild.get("name")
            or "?"
        )

        return escape(
            name[:1].upper()
        )

    # -----------------------------------------------------
    # AVAILABLE SERVERS
    # (listed first, per layout rules above)
    # -----------------------------------------------------

    available_html = ""

    for guild in available:

        guild_id = str(
            guild.get("id")
        )

        guild_name = escape(
            guild.get("name")
            or "Unnamed Server"
        )

        icon = guild_icon(
            guild
        )

        has_permission = user_can_manage_guild(
            guild
        )

        if has_permission:

            action_html = f"""
            <a
                class="button"
                href="/install/{guild_id}"
            >
                ➕ Add Misuki
            </a>
            """

        else:

            action_html = """
            <span
                class="button disabled"
                aria-disabled="true"
                title="You need Manage Server or Administrator permission"
            >
                🔒 Missing Permissions
            </span>
            """

        available_html += f"""

        <div class="server">

            <div class="server-header">

                <div class="server-icon">
                    {icon}
                </div>

                <div>

                    <div class="server-name">
                        {guild_name}
                    </div>

                    <div class="server-id">
                        {escape(guild_id)}
                    </div>

                </div>

            </div>

            <span class="badge badge-yellow">
                Available
            </span>

            <div class="actions">

                {action_html}

            </div>

        </div>

        """

    if not available_html:

        available_html = """
        <div class="notice">

            No additional servers are available
            for Misuki to be added to.

        </div>
        """

    # -----------------------------------------------------
    # AUTHORIZED SERVERS
    # (listed second, per layout rules above)
    # -----------------------------------------------------

    authorized_html = ""

    for guild in authorized:

        guild_id = str(
            guild.get("id")
        )

        guild_name = escape(
            guild.get("name")
            or "Unnamed Server"
        )

        icon = guild_icon(
            guild
        )

        has_permission = user_can_manage_guild(
            guild
        )

        license_info = license_status(
            guild_id
        )

        if license_info["licensed"]:

            license_badge = """
            <span class="badge badge-green">
                ✓ Licensed
            </span>
            """

        elif license_info["status"] == "expired":

            license_badge = """
            <span class="badge badge-red">
                ⚠ License Expired
            </span>
            """

        else:

            license_badge = """
            <span class="badge badge-yellow">
                ⚠ No License
            </span>
            """

        # ---------------------------------------------
        # EXPIRATION DATE PREVIEW
        #
        # Shown directly on the card so the most
        # important detail (when the license ends)
        # doesn't require an extra click.
        # ---------------------------------------------

        expiry_html = ""

        expires_at = license_info.get(
            "expires_at"
        )

        if expires_at:

            try:

                expiration = datetime.fromisoformat(
                    expires_at
                )

                expiry_text = expiration.strftime(
                    "%d/%m/%Y"
                )

                expiry_html = f"""
                <div class="server-id">
                    Expires: {escape(expiry_text)}
                </div>
                """

            except (
                ValueError,
                TypeError
            ):

                pass

        if has_permission:

            action_html = f"""
            <a
                class="button green"
                href="/manage/{guild_id}"
            >
                ⚙ Manage
            </a>
            """

        else:

            action_html = """
            <span
                class="badge badge-gray"
                title="You need Manage Server or Administrator permission"
            >
                🔒 No Permission
            </span>
            """

        authorized_html += f"""

        <div class="server">

            <div class="server-header">

                <div class="server-icon">
                    {icon}
                </div>

                <div>

                    <div class="server-name">
                        {guild_name}
                    </div>

                    <div class="server-id">
                        {escape(guild_id)}
                    </div>

                    {expiry_html}

                </div>

            </div>

            <span class="badge badge-green">
                ✓ Misuki Installed
            </span>

            {license_badge}

            <div class="actions">

                {action_html}

            </div>

        </div>

        """

    if not authorized_html:

        authorized_html = """
        <div class="notice">

            Misuki is not installed in any of
            your servers yet.

        </div>
        """

    # -----------------------------------------------------
    # DASHBOARD CONTENT
    # -----------------------------------------------------

    content = f"""

    <div class="card">

        <div class="profile">

            {profile_html}

            <div>

                <h2 style="margin:0;">
                    Welcome, {username}! 👋
                </h2>

                <p style="margin-bottom:0;">
                    Manage your Discord servers
                    and Misuki installations.
                </p>

            </div>

        </div>

    </div>


    <!-- =================================================
         AVAILABLE (shown first)
         ================================================= -->

    <div class="card">

        <h2>
            🟡 Available Servers
        </h2>

        <p>
            These servers can be connected to Misuki.
            You need Manage Server or Administrator
            permission to add the bot.
        </p>

        <div class="server-grid">

            {available_html}

        </div>

    </div>


    <!-- =================================================
         AUTHORIZED (shown second)
         ================================================= -->

    <div class="card">

        <h2>
            🟢 Authorized Servers
        </h2>

        <p>
            Misuki is already installed in these
            servers. Select "Manage" to view license
            details, including the expiration date.
        </p>

        <div class="server-grid">

            {authorized_html}

        </div>

    </div>

    """

    return page(
        "Dashboard",
        content
        + COOKIE_BANNER
    )


# =========================================================
# MANAGE SERVER
# =========================================================

@app.route(
    "/manage/<guild_id>"
)
def manage(
    guild_id
):

    current = get_current_web_session()

    if current is None:

        return redirect(
            url_for(
                "login"
            )
        )

    # -----------------------------------------------------
    # NORMALIZE GUILD ID
    # -----------------------------------------------------

    try:

        guild_id = str(
            int(guild_id)
        )

    except (
        TypeError,
        ValueError
    ):

        return page(
            "Invalid Server",
            """
            <div class="card center">

                <h1>
                    ❌ Invalid Server
                </h1>

                <p>
                    The server ID is invalid.
                </p>

                <a
                    class="button"
                    href="/dashboard"
                >
                    Back to Dashboard
                </a>

            </div>
            """
        ), 400

    # -----------------------------------------------------
    # CHECK USER SERVER
    # -----------------------------------------------------

    guild = get_user_guild(
        current,
        guild_id
    )

    if guild is None:

        return page(
            "Access Denied",
            """
            <div class="card center">

                <h1>
                    🔒 Access Denied
                </h1>

                <p>
                    You do not have access to this server.
                </p>

                <a
                    class="button"
                    href="/dashboard"
                >
                    Back to Dashboard
                </a>

            </div>
            """
        ), 403

    # -----------------------------------------------------
    # CHECK MANAGE PERMISSION
    #
    # Authoritative server-side check. The dashboard only
    # shows a "No Permission" badge instead of the
    # "Manage" button as a UX hint; this is what actually
    # blocks access.
    # -----------------------------------------------------

    if not user_can_manage_guild(
        guild
    ):

        return page(
            "Permission Required",
            """
            <div class="card center">

                <h1>
                    🔒 Permission Required
                </h1>

                <p>
                    You need Manage Server or
                    Administrator permission.
                </p>

                <a
                    class="button"
                    href="/dashboard"
                >
                    Back to Dashboard
                </a>

            </div>
            """
        ), 403

    # -----------------------------------------------------
    # CHECK BOT INSTALLATION
    # -----------------------------------------------------

    bot_guild_ids = get_bot_guild_ids()

    if guild_id not in bot_guild_ids:

        return redirect(
            url_for(
                "install_bot",
                guild_id=guild_id
            )
        )

    # -----------------------------------------------------
    # LICENSE
    # -----------------------------------------------------

    license_info = license_status(
        guild_id
    )

    if license_info["licensed"]:

        license_status_html = """
        <span class="badge badge-green">
            ✓ Active
        </span>
        """

        expires_at = license_info.get(
            "expires_at"
        )

        if expires_at:

            try:

                expiration = datetime.fromisoformat(
                    expires_at
                )

                expiration_text = (
                    expiration.strftime(
                        "%d/%m/%Y %H:%M UTC"
                    )
                )

            except (
                ValueError,
                TypeError
            ):

                expiration_text = escape(
                    str(expires_at)
                )

        else:

            expiration_text = "No expiration"

    elif license_info["status"] == "expired":

        license_status_html = """
        <span class="badge badge-red">
            ✕ Expired
        </span>
        """

        expiration_text = "License expired"

    else:

        license_status_html = """
        <span class="badge badge-yellow">
            ⚠ Not Licensed
        </span>
        """

        expiration_text = "No active license"

    guild_name = escape(
        guild.get(
            "name"
        )
        or "Discord Server"
    )

    content = f"""

    <div class="card">

        <h1>
            ⚙ {guild_name}
        </h1>

        <p>
            Manage your Misuki installation.
        </p>

        <div class="notice">

            <strong>
                Server ID:
            </strong>

            {escape(guild_id)}

            <br><br>

            <strong>
                Bot:
            </strong>

            <span class="badge badge-green">
                ✓ Installed
            </span>

            <br>

            <strong>
                License:
            </strong>

            {license_status_html}

            <br><br>

            <strong>
                Expiration Date:
            </strong>

            {escape(expiration_text)}

        </div>

        <div class="actions">

            <a
                class="button secondary"
                href="/dashboard"
            >
                ← Dashboard
            </a>

        </div>

    </div>

    """

    return page(
        f"Manage {guild_name}",
        content
        + COOKIE_BANNER
    )


# =========================================================
# REVIEWS PAGE
# =========================================================

@app.route(
    "/review",
    methods=["GET", "POST"]
)
def review():

    current = get_current_web_session()

    # -----------------------------------------------------
    # POST REVIEW
    # -----------------------------------------------------

    if request.method == "POST":

        if current is None:

            return redirect(
                url_for(
                    "login"
                )
            )

        user = current.get(
            "user",
            {}
        )

        user_id = user.get(
            "id"
        )

        username = (
            user.get("global_name")
            or user.get("username")
            or "Discord User"
        )

        if not user_id:

            return page(
                "Review Error",
                """
                <div class="card center">

                    <h1>
                        ❌ Review Error
                    </h1>

                    <p>
                        Your Discord account could
                        not be identified.
                    </p>

                </div>
                """
            ), 400

        if not can_user_review(
            user_id
        ):

            return page(
                "Review Not Available",
                """
                <div class="card center">

                    <h1>
                        🔒 Review Unavailable
                    </h1>

                    <p>
                        You need to have an active
                        Misuki license on a server
                        you manage before submitting
                        a review.
                    </p>

                    <a
                        class="button"
                        href="/dashboard"
                    >
                        Dashboard
                    </a>

                </div>
                """
            ), 403

        guild_id = request.form.get(
            "guild_id"
        )

        rating = request.form.get(
            "rating",
            "5"
        )

        review_text = request.form.get(
            "review",
            ""
        ).strip()

        # -------------------------------------------------
        # VALIDATE RATING
        # -------------------------------------------------

        try:

            rating = int(
                rating
            )

        except (
            TypeError,
            ValueError
        ):

            rating = 0

        if rating < 1 or rating > 5:

            return page(
                "Invalid Rating",
                """
                <div class="card center">

                    <h1>
                        ❌ Invalid Rating
                    </h1>

                    <p>
                        Rating must be between
                        1 and 5 stars.
                    </p>

                    <a
                        class="button"
                        href="/review"
                    >
                        Back
                    </a>

                </div>
                """
            ), 400

        # -------------------------------------------------
        # VALIDATE TEXT
        # -------------------------------------------------

        if not review_text:

            return page(
                "Empty Review",
                """
                <div class="card center">

                    <h1>
                        ❌ Empty Review
                    </h1>

                    <p>
                        Please write something
                        before submitting.
                    </p>

                    <a
                        class="button"
                        href="/review"
                    >
                        Back
                    </a>

                </div>
                """
            ), 400

        if len(review_text) > 1000:

            return page(
                "Review Too Long",
                """
                <div class="card center">

                    <h1>
                        ❌ Review Too Long
                    </h1>

                    <p>
                        Your review must contain
                        1000 characters or fewer.
                    </p>

                    <a
                        class="button"
                        href="/review"
                    >
                        Back
                    </a>

                </div>
                """
            ), 400

        # -------------------------------------------------
        # FIND A VALID LICENSED SERVER
        # -------------------------------------------------

        selected_guild = None

        for guild in current.get(
            "guilds",
            []
        ):

            gid = guild.get(
                "id"
            )

            if guild_id and str(
                gid
            ) != str(
                guild_id
            ):

                continue

            if not user_can_manage_guild(
                guild
            ):

                continue

            license_info = license_status(
                gid
            )

            if license_info["licensed"]:

                selected_guild = str(
                    gid
                )

                break

        if selected_guild is None:

            return page(
                "Invalid Server",
                """
                <div class="card center">

                    <h1>
                        ❌ Invalid Server
                    </h1>

                    <p>
                        Select a server with an
                        active Misuki license.
                    </p>

                    <a
                        class="button"
                        href="/review"
                    >
                        Back
                    </a>

                </div>
                """
            ), 400

        add_review(
            user_id,
            username,
            selected_guild,
            rating,
            review_text
        )

        return redirect(
            url_for(
                "review"
            )
        )

    # -----------------------------------------------------
    # GET REVIEWS
    # -----------------------------------------------------

    reviews = get_reviews(
        20
    )

    review_html = render_reviews(
        reviews
    )

    # -----------------------------------------------------
    # REVIEW FORM
    # -----------------------------------------------------

    form_html = ""

    if current is not None:

        licensed_guilds = []

        for guild in current.get(
            "guilds",
            []
        ):

            gid = guild.get(
                "id"
            )

            if not gid:
                continue

            if not user_can_manage_guild(
                guild
            ):
                continue

            license_info = license_status(
                gid
            )

            if license_info["licensed"]:

                licensed_guilds.append(
                    guild
                )

        if licensed_guilds:

            options = ""

            for guild in licensed_guilds:

                gid = escape(
                    str(
                        guild.get("id")
                    )
                )

                name = escape(
                    guild.get("name")
                    or "Server"
                )

                options += f"""
                <option value="{gid}">
                    {name}
                </option>
                """

            form_html = f"""

            <div class="card">

                <h2>
                    ✍️ Leave a Review
                </h2>

                <form
                    method="POST"
                    action="/review"
                >

                    <label>
                        Server
                    </label>

                    <select
                        class="form-input"
                        name="guild_id"
                        required
                    >
                        {options}
                    </select>

                    <label>
                        Rating
                    </label>

                    <select
                        class="form-input"
                        name="rating"
                        required
                    >

                        <option value="5">
                            ⭐⭐⭐⭐⭐ — 5
                        </option>

                        <option value="4">
                            ⭐⭐⭐⭐☆ — 4
                        </option>

                        <option value="3">
                            ⭐⭐⭐☆☆ — 3
                        </option>

                        <option value="2">
                            ⭐⭐☆☆☆ — 2
                        </option>

                        <option value="1">
                            ⭐☆☆☆☆ — 1
                        </option>

                    </select>

                    <label>
                        Review
                    </label>

                    <textarea
                        class="form-input"
                        name="review"
                        maxlength="1000"
                        placeholder="Tell us what you think about Misuki..."
                        required
                    ></textarea>

                    <button
                        class="button"
                        type="submit"
                    >
                        ⭐ Submit Review
                    </button>

                </form>

            </div>

            """

        else:

            form_html = """
            <div class="notice">

                You need an active Misuki license
                on a server you manage to leave
                a review.

            </div>
            """

    else:

        form_html = """
        <div class="notice">

            🎮
            <a
                href="/login"
                style="
                    color:#8ea0ff;
                    text-decoration:none;
                "
            >
                Log in with Discord
            </a>
            to leave a review.

        </div>
        """

    content = f"""

    <div class="card center">

        <h1>
            ⭐ Misuki Reviews
        </h1>

        <p>
            See what Discord server owners think
            about Misuki.
        </p>

    </div>

    {form_html}

    <div class="card">

        <h2>
            💬 Community Reviews
        </h2>

        <div class="review-grid">

            {review_html}

        </div>

    </div>

    """

    return page(
        "Reviews",
        content
        + COOKIE_BANNER
    )


# =========================================================
# LIKE REVIEW
# =========================================================

@app.route(
    "/like/<int:review_id>",
    methods=["POST"]
)
def like_review(
    review_id
):

    current = get_current_web_session()

    if current is None:

        return redirect(
            url_for(
                "login"
            )
        )

    user = current.get(
        "user",
        {}
    )

    user_id = user.get(
        "id"
    )

    if not user_id:

        return redirect(
            url_for(
                "review"
            )
        )

    try:

        toggle_like(
            review_id,
            user_id
        )

    except psycopg2.Error as error:

        print(
            "Could not toggle review like:",
            error
        )

    return redirect(
        request.referrer
        or url_for(
            "review"
        )
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route(
    "/logout"
)
def logout():

    session_id = session.get(
        "sid"
    )

    if session_id:

        delete_web_session(
            session_id
        )

    session.clear()

    return redirect(
        url_for(
            "home"
        )
    )


# =========================================================
# COOKIES / TERMS / PRIVACY
# =========================================================

@app.route(
    "/cookies"
)
def cookies():

    content = """

    <div class="card legal">

        <h1>
            🍪 Cookies
        </h1>

        <p>
            Misuki uses cookies and browser storage
            to provide essential website functionality.
        </p>


        <h2>
            Essential Cookies
        </h2>

        <p>
            The Misuki session cookie is used to keep
            you signed in and maintain your authenticated
            website session.
        </p>


        <h2 id="terms">
            Terms of Service
        </h2>

        <p>
            By using Misuki, you agree to use the
            service responsibly and in accordance
            with Discord's rules and applicable law.
        </p>


        <h2 id="privacy">
            Privacy Policy
        </h2>

        <p>
            When you authenticate with Discord, Misuki
            receives information necessary to identify
            your Discord account and determine which
            servers you can manage.
        </p>

        <p>
            Information required for the website session
            may be stored temporarily in the Misuki
            database.
        </p>

        <p>
            Misuki does not request unnecessary Discord
            permissions for website authentication.
        </p>


        <h2>
            Cookie Preferences
        </h2>

        <p>
            You can change your cookie preference by
            clearing the Misuki cookie preference from
            your browser's local storage.
        </p>

    </div>

    """

    return page(
        "Cookies & Privacy",
        content
        + COOKIE_BANNER
    )


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def not_found(
    error
):

    return page(
        "Page Not Found",
        """
        <div class="card center">

            <div class="logo">
                🌸
            </div>

            <h1>
                404
            </h1>

            <p>
                The page you're looking for
                doesn't exist.
            </p>

            <a
                class="button"
                href="/"
            >
                🏠 Return Home
            </a>

        </div>
        """
    ), 404


@app.errorhandler(500)
def internal_error(
    error
):

    traceback.print_exc()

    return page(
        "Server Error",
        """
        <div class="card center">

            <div class="logo">
                ⚠️
            </div>

            <h1>
                Something went wrong
            </h1>

            <p>
                Misuki encountered an internal
                server error.
            </p>

            <a
                class="button"
                href="/"
            >
                🏠 Return Home
            </a>

        </div>
        """
    ), 500


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    port = int(
        os.getenv(
            "PORT",
            "5000"
        )
    )

    host = os.getenv(
        "HOST",
        "0.0.0.0"
    )

    print(
        "=========================================="
    )

    print(
        "🌸 Misuki Web Server"
    )

    print(
        f"Running on {host}:{port}"
    )

    print(
        "=========================================="
    )

    app.run(
        host=host,
        port=port,
        debug=False
    )