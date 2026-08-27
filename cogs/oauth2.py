
# =========================================================
# MISUKI DASHBOARD
#
# Discord Login OAuth2
# Bot Installation OAuth2
# Dashboard
# Licenses
# Reviews
# Likes
# Cookies
#
# IMPORTANT:
#
# 1. Discord Login:
#       /login
#       -> Official Discord OAuth2 page
#       -> /login/callback
#
# 2. Bot Installation:
#       /install/<guild_id>
#       -> Discord bot authorization page
#       -> NO redirect_uri
#       -> NO login callback
#
# The two OAuth2 flows are completely separate.
# =========================================================

import os
import json
import secrets
import sqlite3
import traceback

from datetime import datetime, timedelta
from html import escape
from urllib.parse import urlencode

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

DATA_DIR = os.path.join(
    PROJECT_DIR,
    "data"
)

DATABASE = os.path.join(
    DATA_DIR,
    "misuki.db"
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

# This redirect URI is ONLY for Discord LOGIN.
LOGIN_REDIRECT_URI = os.getenv(
    "DISCORD_REDIRECT_URI"
)

FLASK_SECRET_KEY = os.getenv(
    "FLASK_SECRET_KEY"
)

BOT_TOKEN = os.getenv(
    "DISCORD_BOT_TOKEN"
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
        "DISCORD_REDIRECT_URI is not configured."
    )


# =========================================================
# DISCORD
# =========================================================

DISCORD_API = (
    "https://discord.com/api/v10"
)

DISCORD_OAUTH_AUTHORIZE = (
    "https://discord.com/oauth2/authorize"
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

app.config["SESSION_COOKIE_SECURE"] = True

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
# DATABASE
# =========================================================

def database():

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    return sqlite3.connect(
        DATABASE
    )


# =========================================================
# DATABASE SETUP
# =========================================================

def create_database():

    with database() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS licenses (

                guild_id INTEGER PRIMARY KEY,

                license_key TEXT UNIQUE NOT NULL,

                status TEXT NOT NULL
                DEFAULT 'active',

                expires_at TEXT,

                created_at TEXT NOT NULL

            )
            """
        )

        connection.execute(
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

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

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

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS review_likes (

                review_id INTEGER NOT NULL,

                user_id TEXT NOT NULL,

                created_at TEXT NOT NULL,

                PRIMARY KEY (
                    review_id,
                    user_id
                )

            )
            """
        )

        # -------------------------------------------------
        # SAFE REVIEW MIGRATION
        # -------------------------------------------------

        cursor = connection.execute(
            "PRAGMA table_info(reviews)"
        )

        columns = {
            row[1]
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

                    connection.execute(
                        sql
                    )

                except sqlite3.Error as error:

                    print(
                        f"Could not add reviews.{column}:",
                        error
                    )

        try:

            connection.execute(
                """
                UPDATE reviews

                SET expires_at = datetime(
                    created_at,
                    ?
                )

                WHERE expires_at IS NULL

                AND created_at IS NOT NULL
                """,
                (
                    f"+{REVIEW_LIFETIME_DAYS} days",
                )
            )

        except sqlite3.Error as error:

            print(
                "Could not migrate review expiration:",
                error
            )

        connection.commit()

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

    now = datetime.utcnow()

    expires = (
        now
        + timedelta(days=30)
    )

    with database() as connection:

        connection.execute(
            """
            INSERT INTO web_sessions
            (
                session_id,
                user_data,
                guild_data,
                created_at,
                expires_at
            )

            VALUES (?, ?, ?, ?, ?)
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

            WHERE session_id = ?
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

    if datetime.utcnow() >= expiration:

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


def delete_web_session(
    session_id
):

    if not session_id:
        return

    with database() as connection:

        connection.execute(
            """
            DELETE FROM web_sessions

            WHERE session_id = ?
            """,
            (
                session_id,
            )
        )

        connection.commit()


def cleanup_sessions():

    now = datetime.utcnow().isoformat()

    with database() as connection:

        connection.execute(
            """
            DELETE FROM web_sessions

            WHERE expires_at < ?
            """,
            (
                now,
            )
        )

        connection.commit()


def get_current_web_session():

    return get_web_session(
        session.get("sid")
    )


# =========================================================
# DISCORD HTTP HELPERS
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


def bot_headers():

    if not BOT_TOKEN:
        return None

    return {
        "Authorization":
            f"Bot {BOT_TOKEN}"
    }


# =========================================================
# DISCORD LOGIN
#
# THIS IS ONLY USER LOGIN.
#
# It does NOT install the bot.
# =========================================================

def discord_login_url():

    state = secrets.token_urlsafe(
        32
    )

    session["login_state"] = state

    session.permanent = True

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
        DISCORD_OAUTH_AUTHORIZE
        + "?"
        + urlencode(params)
    )


@app.route("/login")
def login():

    return redirect(
        discord_login_url()
    )


@app.route("/login/callback")
def login_callback():

    error = request.args.get(
        "error"
    )

    if error:

        session.pop(
            "login_state",
            None
        )

        return page(
            "Login Cancelled",
            """
            <div class="card center">

                <h1>
                    ❌ Login Cancelled
                </h1>

                <p>
                    Discord login was cancelled.
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

    state = request.args.get(
        "state"
    )

    expected_state = session.pop(
        "login_state",
        None
    )

    if (
        not state
        or not expected_state
        or not secrets.compare_digest(
            state,
            expected_state
        )
    ):

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Invalid Login
                </h1>

                <p>
                    The Discord login request
                    could not be verified.
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

                <a
                    class="button"
                    href="/"
                >
                    Return Home
                </a>

            </div>
            """
        ), 400

    # -----------------------------------------------------
    # EXCHANGE LOGIN CODE
    # -----------------------------------------------------

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
                    ❌ Discord Rejected Login
                </h1>

                <p>
                    Discord rejected the login request.
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
        ), 500

    access_token = token_json.get(
        "access_token"
    )

    if not access_token:

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ No Access Token
                </h1>

                <p>
                    Discord did not provide an
                    access token.
                </p>

            </div>
            """
        ), 400

    # -----------------------------------------------------
    # GET USER
    # -----------------------------------------------------

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
            "Discord user request failed:",
            error
        )

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Discord Connection Error
                </h1>

            </div>
            """
        ), 500

    if user_response.status_code != 200:

        print(
            "Discord user response:",
            user_response.status_code,
            user_response.text
        )

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Could Not Get Discord Account
                </h1>

            </div>
            """
        ), 400

    if guild_response.status_code != 200:

        print(
            "Discord guild response:",
            guild_response.status_code,
            guild_response.text
        )

        return page(
            "Login Error",
            """
            <div class="card center">

                <h1>
                    ❌ Could Not Get Discord Servers
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
        ), 500

    # -----------------------------------------------------
    # CREATE WEBSITE SESSION
    # -----------------------------------------------------

    cleanup_sessions()

    old_session = session.get(
        "sid"
    )

    if old_session:

        delete_web_session(
            old_session
        )

    session_id = create_web_session(
        user,
        guilds
    )

    session.clear()

    session.permanent = True

    session["sid"] = session_id

    return redirect(
        url_for(
            "dashboard"
        )
    )


# =========================================================
# BOT INSTALLATION
#
# THIS IS NOT USER LOGIN.
#
# NO redirect_uri.
# NO response_type.
# NO callback.
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
        DISCORD_OAUTH_AUTHORIZE
        + "?"
        + urlencode(params)
    )


# =========================================================
# BOT GUILDS
# =========================================================

def get_bot_guild_ids():

    if not BOT_TOKEN:

        print(
            "DISCORD_BOT_TOKEN not configured."
        )

        return set()

    try:

        response = requests.get(

            f"{DISCORD_API}/users/@me/guilds",

            headers=bot_headers(),

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
# LICENSE
# =========================================================

def get_license(
    guild_id
):

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

            WHERE guild_id = ?
            """,
            (
                int(guild_id),
            )
        )

        return cursor.fetchone()


def set_license_expired(
    guild_id
):

    with database() as connection:

        connection.execute(
            """
            UPDATE licenses

            SET status = 'expired'

            WHERE guild_id = ?
            """,
            (
                int(guild_id),
            )
        )

        connection.commit()


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

            if datetime.now() >= expiration:

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
# REVIEWS
# =========================================================

def cleanup_reviews():

    now = datetime.utcnow().isoformat()

    with database() as connection:

        connection.execute(
            """
            DELETE FROM reviews

            WHERE expires_at IS NOT NULL

            AND expires_at < ?
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

            LIMIT ?
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

    for guild in session_data.get(
        "guilds",
        []
    ):

        guild_id = guild.get(
            "id"
        )

        if not guild_id:
            continue

        if license_status(
            guild_id
        )["licensed"]:

            return True

    return False


def add_review(
    user_id,
    username,
    guild_id,
    rating,
    review_text
):

    now = datetime.utcnow()

    expires = (
        now
        + timedelta(
            days=REVIEW_LIFETIME_DAYS
        )
    )

    with database() as connection:

        connection.execute(
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

            VALUES (?, ?, ?, ?, ?, 0, ?, ?)
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


def toggle_like(
    review_id,
    user_id
):

    with database() as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT 1

            FROM review_likes

            WHERE review_id = ?

            AND user_id = ?
            """,
            (
                review_id,
                str(user_id)
            )
        )

        existing = cursor.fetchone()

        if existing:

            connection.execute(
                """
                DELETE FROM review_likes

                WHERE review_id = ?

                AND user_id = ?
                """,
                (
                    review_id,
                    str(user_id)
                )
            )

            connection.execute(
                """
                UPDATE reviews

                SET likes = MAX(likes - 1, 0)

                WHERE id = ?
                """,
                (
                    review_id,
                )
            )

        else:

            connection.execute(
                """
                INSERT INTO review_likes
                (
                    review_id,
                    user_id,
                    created_at
                )

                VALUES (?, ?, ?)
                """,
                (
                    review_id,
                    str(user_id),
                    datetime.utcnow().isoformat()
                )
            )

            connection.execute(
                """
                UPDATE reviews

                SET likes = likes + 1

                WHERE id = ?
                """,
                (
                    review_id,
                )
            )

        connection.commit()


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
            🔵 Sign In with Discord
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

        rating = max(
            1,
            min(
                5,
                int(rating)
            )
        )

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

                <a
                    class="like-button"
                    href="/like/{review_id}"
                >
                    👍 {likes}
                </a>

            </div>

        </div>

        """

    return html


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    cleanup_reviews()

    reviews = get_reviews(
        HOME_REVIEW_COUNT
    )

    reviews_html = render_reviews(
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
            A modern Discord management dashboard
            for your servers.
        </p>

        <a
            class="button"
            href="/login"
        >
            🔵 Sign In with Discord
        </a>

    </div>

    <div class="card">

        <h2>
            ⭐ What people say about Misuki
        </h2>

        <p>
            Reviews from Misuki users.
        </p>

        <div class="review-grid">

            {reviews_html}

        </div>

    </div>

    """

    return page(
        "Home",
        content + COOKIE_BANNER
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    current = get_current_web_session()

    if current is None:

        return page(
            "Dashboard",
            """
            <div class="card center">

                <div class="logo">
                    🌸
                </div>

                <h1>
                    Misuki Dashboard
                </h1>

                <p>
                    Sign in with Discord to access
                    your Misuki dashboard.
                </p>

                <a
                    class="button"
                    href="/login"
                >
                    🔵 Sign In with Discord
                </a>

            </div>
            """
        )

    user = current["user"]

    guilds = current["guilds"]

    bot_guild_ids = get_bot_guild_ids()

    username = (
        user.get("global_name")
        or user.get("username")
        or "Discord User"
    )

    user_id = str(
        user.get(
            "id",
            ""
        )
    )

    avatar = user.get(
        "avatar"
    )

    if avatar:

        avatar_url = (
            "https://cdn.discordapp.com/"
            f"avatars/{user_id}/{avatar}.png"
        )

    else:

        avatar_url = (
            "https://cdn.discordapp.com/"
            "embed/avatars/0.png"
        )

    authorized = []

    available = []

    for guild in guilds:

        guild_id = str(
            guild.get(
                "id",
                ""
            )
        )

        if guild_id in bot_guild_ids:

            authorized.append(
                guild
            )

        elif user_can_manage_guild(
            guild
        ):

            available.append(
                guild
            )

    # =====================================================
    # SERVER CARD
    # =====================================================

    def render_server(
        guild,
        installed
    ):

        guild_id = str(
            guild.get(
                "id",
                ""
            )
        )

        guild_name = escape(
            guild.get(
                "name",
                "Unknown Server"
            )
        )

        license_info = license_status(
            guild_id
        )

        licensed = license_info[
            "licensed"
        ]

        status = license_info[
            "status"
        ]

        if licensed:

            license_badge = """
            <span class="badge badge-green">
                🟢 LICENSED
            </span>
            """

        elif status == "expired":

            license_badge = """
            <span class="badge badge-red">
                🔴 LICENSE EXPIRED
            </span>
            """

        elif status == "revoked":

            license_badge = """
            <span class="badge badge-red">
                ⛔ LICENSE REVOKED
            </span>
            """

        else:

            license_badge = """
            <span class="badge badge-yellow">
                🟡 NO LICENSE
            </span>
            """

        expiration_html = ""

        expires_at = license_info[
            "expires_at"
        ]

        if expires_at:

            try:

                expiration = datetime.fromisoformat(
                    expires_at
                )

                timestamp = int(
                    expiration.timestamp()
                )

                expiration_html = f"""

                <div
                    style="
                        margin-top:10px;
                        color:#858a98;
                        font-size:12px;
                    "
                >

                    📅 Expires:

                    <strong>
                        <t:{timestamp}:F>
                    </strong>

                </div>

                """

            except (
                ValueError,
                TypeError
            ):

                expiration_html = ""

        # -------------------------------------------------
        # SERVER ICON
        # -------------------------------------------------

        guild_icon = guild.get(
            "icon"
        )

        if guild_icon:

            icon_url = (
                "https://cdn.discordapp.com/"
                f"icons/{guild_id}/{guild_icon}.png"
            )

            icon_html = f"""
            <img
                class="server-icon"
                src="{escape(icon_url)}"
                alt="Server icon"
            >
            """

        else:

            first_letter = escape(
                (
                    guild.get(
                        "name",
                        "?"
                    )[:1]
                    or "?"
                ).upper()
            )

            icon_html = f"""
            <div class="server-icon">
                {first_letter}
            </div>
            """

        # -------------------------------------------------
        # INSTALLATION
        # -------------------------------------------------

        if installed:

            installation_badge = """
            <span class="badge badge-green">
                ✓ MISUKI INSTALLED
            </span>
            """

            installation_button = f"""
            <a
                class="button secondary"
                href="/manage/{escape(guild_id)}"
            >
                ⚙️ Manage
            </a>
            """

        else:

            installation_badge = """
            <span class="badge badge-yellow">
                ⚠️ MISUKI NOT INSTALLED
            </span>
            """

            invite = bot_install_url(
                guild_id
            )

            installation_button = f"""
            <a
                class="button green"
                href="{escape(invite)}"
            >
                ➕ Add Misuki
            </a>
            """

        return f"""

        <div class="server">

            <div class="server-header">

                {icon_html}

                <div>

                    <div class="server-name">
                        {guild_name}
                    </div>

                    <div class="server-id">
                        ID: {escape(guild_id)}
                    </div>

                </div>

            </div>

            <div>

                {license_badge}

                {installation_badge}

                {expiration_html}

            </div>

            <div class="actions">

                {installation_button}

            </div>

        </div>

        """

    # =====================================================
    # AUTHORIZED FIRST
    # =====================================================

    authorized_html = ""

    for guild in authorized:

        authorized_html += render_server(
            guild,
            True
        )

    if not authorized_html:

        authorized_html = """
        <div class="notice">
            You currently have no servers where
            Misuki is installed.
        </div>
        """

    # =====================================================
    # AVAILABLE SECOND
    # =====================================================

    available_html = ""

    for guild in available:

        available_html += render_server(
            guild,
            False
        )

    if not available_html:

        available_html = """
        <div class="notice">
            There are currently no available
            servers where you can install Misuki.
        </div>
        """

    content = f"""

    <div class="card">

        <div class="profile">

            <img
                class="avatar"
                src="{escape(avatar_url)}"
                alt="Discord Avatar"
            >

            <div>

                <h2 style="margin:0;">
                    Welcome, {escape(username)}
                </h2>

                <p style="margin:5px 0 0;">

                    Discord ID:

                    <code>
                        {escape(user_id)}
                    </code>

                </p>

            </div>

        </div>

    </div>

    <div class="card">

        <h2>
            🟢 Authorized Servers
        </h2>

        <p>
            Servers where Misuki is already installed.
        </p>

        <div class="server-grid">

            {authorized_html}

        </div>

    </div>

    <div class="card">

        <h2>
            ➕ Available Servers
        </h2>

        <p>
            Servers where you can add Misuki.
        </p>

        <div class="server-grid">

            {available_html}

        </div>

    </div>

    <div style="text-align:center;">

        <a
            class="button"
            href="/review"
        >
            ⭐ Leave a Review
        </a>

    </div>

    """

    return page(
        "Dashboard",
        content + COOKIE_BANNER
    )


# =========================================================
# MANAGE
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
                "dashboard"
            )
        )

    guild = None

    for item in current["guilds"]:

        if str(
            item.get("id")
        ) == str(guild_id):

            guild = item

            break

    if guild is None:

        return page(
            "Access Denied",
            """
            <div class="card center">

                <h1>
                    🔒 Access Denied
                </h1>

                <a
                    class="button"
                    href="/dashboard"
                >
                    Back to Dashboard
                </a>

            </div>
            """
        ), 403

    guild_name = escape(
        guild.get(
            "name",
            "Discord Server"
        )
    )

    info = license_status(
        guild_id
    )

    expiration_text = "Never"

    if info["expires_at"]:

        try:

            expiration = datetime.fromisoformat(
                info["expires_at"]
            )

            expiration_text = (
                expiration.strftime(
                    "%d/%m/%Y %H:%M"
                )
            )

        except (
            ValueError,
            TypeError
        ):

            expiration_text = str(
                info["expires_at"]
            )

    content = f"""

    <div class="card">

        <h1>
            ⚙️ Manage {guild_name}
        </h1>

        <p>
            Misuki server management.
        </p>

        <div class="notice">

            <strong>
                License status:
            </strong>

            {escape(info["status"])}

            <br><br>

            <strong>
                📅 Expiration:
            </strong>

            {escape(
                str(expiration_text)
            )}

        </div>

        <a
            class="button secondary"
            href="/dashboard"
        >
            ← Back to Dashboard
        </a>

    </div>

    """

    return page(
        "Manage",
        content + COOKIE_BANNER
    )


# =========================================================
# REVIEW PAGE
# =========================================================

@app.route("/review")
def review_page():

    current = get_current_web_session()

    if current is None:

        return redirect(
            url_for(
                "login"
            )
        )

    user = current["user"]

    user_id = str(
        user.get(
            "id",
            ""
        )
    )

    if not can_user_review(
        user_id
    ):

        return page(
            "Review",
            """
            <div class="card center">

                <h1>
                    🔒 Review Unavailable
                </h1>

                <p>
                    You can only leave a review
                    after having an active Misuki
                    license.
                </p>

                <a
                    class="button"
                    href="/dashboard"
                >
                    Back to Dashboard
                </a>

            </div>
            """
        )

    guild_options = ""

    for guild in current["guilds"]:

        guild_id = guild.get(
            "id"
        )

        if not guild_id:
            continue

        if license_status(
            guild_id
        )["licensed"]:

            guild_options += f"""
            <option value="{escape(str(guild_id))}">
                {escape(
                    guild.get(
                        "name",
                        "Server"
                    )
                )}
            </option>
            """

    content = f"""

    <div class="card">

        <h1>
            ⭐ Leave a Review
        </h1>

        <p>
            Tell us what you think about Misuki.
        </p>

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

                {guild_options}

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
                    ⭐⭐⭐⭐⭐
                </option>

                <option value="4">
                    ⭐⭐⭐⭐
                </option>

                <option value="3">
                    ⭐⭐⭐
                </option>

                <option value="2">
                    ⭐⭐
                </option>

                <option value="1">
                    ⭐
                </option>

            </select>

            <label>
                Review
            </label>

            <textarea
                class="form-input"
                name="review"
                maxlength="1000"
                placeholder="Write your review..."
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

    return page(
        "Review",
        content + COOKIE_BANNER
    )


# =========================================================
# SUBMIT REVIEW
# =========================================================

@app.route(
    "/review",
    methods=["POST"]
)
def submit_review():

    current = get_current_web_session()

    if current is None:

        return redirect(
            url_for(
                "login"
            )
        )

    user = current["user"]

    user_id = str(
        user.get(
            "id",
            ""
        )
    )

    if not can_user_review(
        user_id
    ):

        return page(
            "Review",
            """
            <div class="card center">

                <h1>
                    🔒 Review Unavailable
                </h1>

                <p>
                    You need an active Misuki
                    license to leave a review.
                </p>

            </div>
            """
        ), 403

    guild_id = request.form.get(
        "guild_id"
    )

    rating = request.form.get(
        "rating"
    )

    review_text = (
        request.form.get(
            "review",
            ""
        )
        .strip()
    )

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
            "Review",
            """
            <div class="card center">

                <h1>
                    ❌ Invalid Rating
                </h1>

                <a
                    class="button"
                    href="/review"
                >
                    Back
                </a>

            </div>
            """
        ), 400

    if not review_text:

        return page(
            "Review",
            """
            <div class="card center">

                <h1>
                    ❌ Review Cannot Be Empty
                </h1>

                <a
                    class="button"
                    href="/review"
                >
                    Back
                </a>

            </div>
            """
        ), 400

    if not guild_id:

        return page(
            "Review",
            """
            <div class="card center">

                <h1>
                    ❌ Server Not Selected
                </h1>

                <a
                    class="button"
                    href="/review"
                >
                    Back
                </a>

            </div>
            """
        ), 400

    if not license_status(
        guild_id
    )["licensed"]:

        return page(
            "Review",
            """
            <div class="card center">

                <h1>
                    🔒 License Required
                </h1>

            </div>
            """
        ), 403

    valid_guild = False

    for guild in current["guilds"]:

        if str(
            guild.get("id")
        ) == str(guild_id):

            valid_guild = True
            break

    if not valid_guild:

        return page(
            "Review",
            """
            <div class="card center">

                <h1>
                    ❌ Invalid Server
                </h1>

            </div>
            """
        ), 403

    username = (
        user.get("global_name")
        or user.get("username")
        or "Discord User"
    )

    add_review(
        user_id,
        username,
        guild_id,
        rating,
        review_text
    )

    return page(
        "Review Submitted",
        """
        <div class="card center">

            <h1>
                ⭐ Thank You!
            </h1>

            <p>
                Your review has been submitted.
            </p>

            <a
                class="button"
                href="/"
            >
                Return Home
            </a>

        </div>
        """
    )


# =========================================================
# LIKE
# =========================================================

@app.route(
    "/like/<int:review_id>"
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

    user = current["user"]

    user_id = str(
        user.get(
            "id",
            ""
        )
    )

    toggle_like(
        review_id,
        user_id
    )

    return redirect(
        request.referrer
        or url_for("home")
    )


# =========================================================
# COOKIES
# =========================================================

@app.route("/cookies")
def cookies():

    content = """

    <div class="card legal">

        <h1>
            Cookie Policy
        </h1>

        <p>
            Last updated: 27 August 2026
        </p>

        <h2>
            1. Essential Cookies
        </h2>

        <p>
            Misuki uses an essential session cookie
            to keep authenticated users signed in.
        </p>

        <h2>
            2. Optional Cookies
        </h2>

        <p>
            Misuki does not currently require
            advertising or analytics cookies.
        </p>

        <h2 id="terms">
            Terms of Service
        </h2>

        <p>
            By accessing or using Misuki, you agree
            to these Terms of Service.
        </p>

        <h2 id="privacy">
            Privacy Policy
        </h2>

        <p>
            Discord information is used only to provide
            the Misuki dashboard and determine which
            servers the user can manage.
        </p>

        <p>
            Misuki does not intentionally sell personal
            information to third parties.
        </p>

    </div>

    """

    return page(
        "Cookies",
        content + COOKIE_BANNER
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
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
# 404
# =========================================================

@app.errorhandler(404)
def not_found(error):

    return page(
        "404",
        """
        <div class="card center">

            <h1>
                404
            </h1>

            <p>
                The page you requested does not exist.
            </p>

            <a
                class="button"
                href="/"
            >
                Return Home
            </a>

        </div>
        """
    ), 404


# =========================================================
# 500
# =========================================================

@app.errorhandler(500)
def internal_error(error):

    print(
        "INTERNAL SERVER ERROR:",
        error
    )

    traceback.print_exc()

    return page(
        "Server Error",
        """
        <div class="card center">

            <h1>
                ❌ Server Error
            </h1>

            <p>
                Something went wrong while processing
                your request.
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


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "Misuki Dashboard starting..."
    )

    print(
        "========================================"
    )

    print(
        f"Client ID loaded: "
        f"{bool(CLIENT_ID)}"
    )

    print(
        f"Client Secret loaded: "
        f"{bool(CLIENT_SECRET)}"
    )

    print(
        f"Flask Secret loaded: "
        f"{bool(FLASK_SECRET_KEY)}"
    )

    print(
        f"Bot Token loaded: "
        f"{bool(BOT_TOKEN)}"
    )

    print(
        f"Login Redirect URI: "
        f"{LOGIN_REDIRECT_URI}"
    )

    print(
        f"Database: "
        f"{DATABASE}"
    )

    print(
        "========================================"
    )

    app.run(
        host="0.0.0.0",

        port=int(
            os.getenv(
                "PORT",
                "5000"
            )
        ),

        debug=False
    )

