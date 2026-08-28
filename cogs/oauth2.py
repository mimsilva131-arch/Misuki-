
import os
import sqlite3
import random
import secrets

from datetime import datetime

import requests

from flask import (
    Flask,
    redirect,
    session,
    request,
    render_template_string
)

from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# CONFIG
# =========================================================

CLIENT_ID = os.getenv(
    "DISCORD_CLIENT_ID"
)

CLIENT_SECRET = os.getenv(
    "DISCORD_CLIENT_SECRET"
)

# OAuth2 used for bot/add authorization
DISCORD_REDIRECT_URI = os.getenv(
    "DISCORD_REDIRECT_URI"
)

# OAuth2 used ONLY for Discord login
DISCORD_LOGIN_REDIRECT_URI = os.getenv(
    "DISCORD_LOGIN_REDIRECT_URI"
)

BOT_TOKEN = os.getenv(
    "DISCORD_TOKEN"
)

DATABASE = os.getenv(
    "DATABASE_PATH",
    "data/misuki.db"
)

SECRET_KEY = os.getenv(
    "FLASK_SECRET_KEY"
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
        "⚠️ A temporary key was generated."
    )

    print(
        "⚠️ Set FLASK_SECRET_KEY permanently in Render."
    )


# =========================================================
# FLASK
# =========================================================

app = Flask(__name__)

app.secret_key = SECRET_KEY

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1
)


# =========================================================
# SESSION
# =========================================================

app.config[
    "SESSION_COOKIE_HTTPONLY"
] = True

app.config[
    "SESSION_COOKIE_SAMESITE"
] = "Lax"

app.config[
    "SESSION_COOKIE_SECURE"
] = True

app.config[
    "SESSION_REFRESH_EACH_REQUEST"
] = True


# =========================================================
# DISCORD
# =========================================================

DISCORD_API = (
    "https://discord.com/api/v10"
)


# =========================================================
# DATABASE
# =========================================================

def database_connection():

    directory = os.path.dirname(
        DATABASE
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    return sqlite3.connect(
        DATABASE
    )


# =========================================================
# REVIEWS DATABASE
# =========================================================

def create_reviews_database():

    with database_connection() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id TEXT NOT NULL,

                username TEXT NOT NULL,

                avatar TEXT,

                review TEXT NOT NULL,

                rating INTEGER NOT NULL,

                created_at TEXT NOT NULL

            )
            """
        )

        connection.commit()


create_reviews_database()


# =========================================================
# LICENSE
# =========================================================

def get_license(guild_id):

    try:

        with database_connection() as connection:

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
                    guild_id,
                )
            )

            return cursor.fetchone()

    except Exception as error:

        print(
            f"❌ License database error: {error}"
        )

        return None


# =========================================================
# ACTIVE LICENSE
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

        try:

            expiration = datetime.fromisoformat(
                expires_at
            )

        except ValueError:

            return False


        if datetime.now() >= expiration:

            try:

                with database_connection() as connection:

                    connection.execute(
                        """
                        UPDATE licenses

                        SET status = 'expired'

                        WHERE guild_id = ?
                        """,
                        (
                            guild_id,
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
# USER LICENSE
# =========================================================

def user_has_license():

    guilds = get_user_guilds()

    for guild in guilds:

        guild_id = guild.get(
            "id"
        )

        if license_is_active(
            guild_id
        ):

            return True

    return False


# =========================================================
# BOT HEADERS
# =========================================================

def discord_bot_headers():

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

    except Exception as error:

        print(
            f"❌ Discord user request error: {error}"
        )

        return None


    if response.status_code != 200:

        return None


    return response.json()


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

    except Exception as error:

        print(
            f"❌ Discord guild request error: {error}"
        )

        return []


    if response.status_code != 200:

        return []


    return response.json()


# =========================================================
# GET BOT GUILDS
# =========================================================

def get_bot_guilds():

    if not BOT_TOKEN:

        print(
            "⚠️ DISCORD_TOKEN is missing."
        )

        return []


    try:

        response = requests.get(

            f"{DISCORD_API}/users/@me/guilds",

            headers=discord_bot_headers(),

            timeout=10

        )

    except Exception as error:

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


    return response.json()


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


    return (

        "https://discord.com/oauth2/authorize"

        f"?client_id={CLIENT_ID}"

        "&scope=bot%20applications.commands"

        f"&permissions={permissions}"

        f"&guild_id={guild_id}"

    )


# =========================================================
# BASE CSS
# =========================================================

BASE_STYLE = """

<style>

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    background:
        radial-gradient(
            circle at top,
            #20263a 0%,
            #0b0d13 45%,
            #07080c 100%
        );

    color: #ffffff;

    font-family:
        Inter,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    min-height: 100vh;
}

a {

    color: inherit;

    text-decoration: none;
}

.container {

    width: min(
        1150px,
        92%
    );

    margin: auto;
}


/* HEADER */

header {

    height: 76px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    border-bottom:
        1px solid rgba(
            255,
            255,
            255,
            .08
        );
}

.logo {

    font-size: 25px;

    font-weight: 800;

    letter-spacing: -1px;
}

.logo span {

    color: #7289da;
}


/* HAMBURGER */

.hamburger {

    width: 45px;

    height: 40px;

    border:
        1px solid rgba(
            255,
            255,
            255,
            .12
        );

    background:
        rgba(
            255,
            255,
            255,
            .04
        );

    border-radius: 10px;

    cursor: pointer;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    gap: 5px;
}

.hamburger span {

    width: 20px;

    height: 2px;

    background: #ffffff;

    border-radius: 5px;
}


/* MENU */

.menu {

    position: fixed;

    top: 0;

    right: -360px;

    width: 350px;

    height: 100vh;

    background: #10131d;

    border-left:
        1px solid rgba(
            255,
            255,
            255,
            .08
        );

    z-index: 1000;

    transition:
        right .25s ease;

    padding: 25px;

    box-shadow:
        -15px 0 40px
        rgba(
            0,
            0,
            0,
            .4
        );

    overflow-y: auto;
}

.menu.open {

    right: 0;
}

.menu-header {

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 25px;
}

.menu-title {

    font-size: 20px;

    font-weight: 700;
}

.menu-close {

    border: none;

    background: transparent;

    color: #ffffff;

    font-size: 25px;

    cursor: pointer;
}

.menu a {

    display: block;

    padding: 14px 0;

    border-bottom:
        1px solid rgba(
            255,
            255,
            255,
            .06
        );

    color: #d7d9e0;

    transition: .15s;
}

.menu a:hover {

    color: #7289da;
}

.menu-section {

    margin-top: 25px;

    margin-bottom: 7px;

    color: #73798a;

    font-size: 11px;

    font-weight: 800;

    text-transform: uppercase;

    letter-spacing: 1px;
}


/* DISCORD LOGIN */

.discord-login {

    display: flex !important;

    align-items: center;

    gap: 10px;

    margin-top: 15px;

    padding:
        13px 16px !important;

    background: #5865f2;

    border-radius: 10px;

    color: #ffffff !important;

    font-weight: 700;

    border: none !important;
}

.discord-login:hover {

    background: #6875ff;

    color: #ffffff !important;
}

.discord-icon {

    width: 21px;

    height: 21px;

    display: block;

    flex-shrink: 0;
}


/* OVERLAY */

.overlay {

    display: none;

    position: fixed;

    inset: 0;

    background:
        rgba(
            0,
            0,
            0,
            .55
        );

    z-index: 999;
}

.overlay.show {

    display: block;
}


/* HERO */

.hero {

    text-align: center;

    padding:
        100px 0 70px;
}

.hero h1 {

    font-size:
        clamp(
            42px,
            7vw,
            76px
        );

    margin: 0;

    letter-spacing: -3px;
}

.hero h1 span {

    color: #7289da;
}

.hero p {

    max-width: 650px;

    margin:
        25px auto;

    color: #aeb3c0;

    font-size: 18px;

    line-height: 1.7;
}

.dashboard-button {

    display: inline-block;

    margin-top: 20px;

    background: #5865f2;

    padding:
        15px 28px;

    border-radius: 12px;

    font-weight: 800;

    transition: .2s;
}

.dashboard-button:hover {

    transform:
        translateY(-2px);

    background: #6875ff;
}


/* SECTIONS */

.section {

    padding:
        55px 0;
}

.section-title {

    font-size: 30px;

    margin-bottom: 25px;
}


/* SERVER GRID */

.server-grid {

    display: grid;

    grid-template-columns:
        repeat(
            auto-fill,
            minmax(
                280px,
                1fr
            )
        );

    gap: 18px;
}

.card {

    background:
        rgba(
            255,
            255,
            255,
            .045
        );

    border:
        1px solid rgba(
            255,
            255,
            255,
            .08
        );

    border-radius: 16px;

    padding: 20px;

    backdrop-filter:
        blur(10px);
}

.server-card {

    display: flex;

    flex-direction: column;

    gap: 15px;
}

.server-top {

    display: flex;

    align-items: center;

    gap: 14px;
}

.server-icon {

    width: 52px;

    height: 52px;

    border-radius: 15px;

    object-fit: cover;

    background: #20232e;
}

.server-icon-placeholder {

    width: 52px;

    height: 52px;

    border-radius: 15px;

    background: #20232e;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 22px;

    font-weight: 800;
}

.server-name {

    font-size: 17px;

    font-weight: 750;

    overflow: hidden;

    text-overflow: ellipsis;

    white-space: nowrap;
}

.server-id {

    font-size: 12px;

    color: #858b9a;
}


/* BUTTONS */

.button {

    display: inline-block;

    text-align: center;

    border-radius: 10px;

    padding:
        11px 15px;

    font-weight: 700;

    border: none;

    cursor: pointer;
}

.manage {

    background: #5865f2;
}

.manage:hover {

    background: #6875ff;
}

.add {

    background: #3ba55d;
}

.add:hover {

    background: #43b968;
}

.blocked {

    background:
        rgba(
            255,
            255,
            255,
            .07
        );

    color: #888e9d;

    cursor: not-allowed;
}


/* REVIEWS */

.review-grid {

    display: grid;

    grid-template-columns:
        repeat(
            auto-fill,
            minmax(
                280px,
                1fr
            )
        );

    gap: 18px;
}

.review-card {

    min-height: 170px;
}

.review-user {

    display: flex;

    align-items: center;

    gap: 12px;

    margin-bottom: 15px;
}

.review-avatar {

    width: 42px;

    height: 42px;

    border-radius: 50%;

    object-fit: cover;
}

.review-text {

    color: #c9ccd5;

    line-height: 1.6;
}

.stars {

    color: #ffd166;

    letter-spacing: 2px;
}


/* EMPTY */

.empty {

    padding: 30px;

    text-align: center;

    border:
        1px dashed rgba(
            255,
            255,
            255,
            .1
        );

    border-radius: 14px;

    color: #858b9a;
}


/* FOOTER */

footer {

    margin-top: 70px;

    padding: 35px 0;

    border-top:
        1px solid rgba(
            255,
            255,
            255,
            .08
        );

    color: #818795;

    text-align: center;
}

.footer-links {

    display: flex;

    justify-content: center;

    gap: 20px;

    flex-wrap: wrap;

    margin-top: 12px;
}

.footer-links a:hover {

    color: #7289da;
}


/* COOKIE */

.cookie {

    position: fixed;

    left: 20px;

    right: 20px;

    bottom: 20px;

    max-width: 900px;

    margin: auto;

    background:
        rgba(
            20,
            23,
            33,
            .98
        );

    border:
        1px solid rgba(
            255,
            255,
            255,
            .1
        );

    border-radius: 18px;

    padding: 22px;

    z-index: 2000;

    box-shadow:
        0 20px 60px
        rgba(
            0,
            0,
            0,
            .45
        );
}

.cookie h3 {

    margin-top: 0;
}

.cookie p {

    color: #aeb3c0;

    line-height: 1.5;
}

.cookie-buttons {

    display: flex;

    gap: 10px;

    flex-wrap: wrap;
}

.cookie-buttons button {

    border: none;

    border-radius: 9px;

    padding:
        11px 16px;

    cursor: pointer;

    font-weight: 700;
}

.accept {

    background: #5865f2;

    color: #ffffff;
}

.essential {

    background: #303442;

    color: #ffffff;
}

.deny {

    background: transparent;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            .15
        ) !important;

    color: #bbbbbb;
}


/* FORM */

.form {

    max-width: 600px;

    margin:
        40px auto;
}

.form textarea,
.form select {

    width: 100%;

    background: #141722;

    color: #ffffff;

    border:
        1px solid rgba(
            255,
            255,
            255,
            .12
        );

    border-radius: 10px;

    padding: 13px;

    margin:
        8px 0 18px;
}

.form textarea {

    min-height: 130px;

    resize: vertical;
}


/* LICENSE */

.license-key {

    font-family: monospace;

    word-break: break-all;

    background: #090b10;

    padding: 12px;

    border-radius: 9px;
}

.status-active {

    color: #57f287;
}

.status-expired {

    color: #ed4245;
}

.status-revoked {

    color: #ed4245;
}


/* RESPONSIVE */

@media (max-width: 600px) {

    .hero {

        padding:
            70px 0 50px;
    }

    .menu {

        width: 90%;
    }

}

</style>

"""


# =========================================================
# HEADER
# =========================================================

HEADER = """

<header class="container">

    <a
        class="logo"
        href="/"
    >
        Misuki<span>.</span>
    </a>


    <button
        class="hamburger"
        onclick="openMenu()"
        aria-label="Open menu"
    >

        <span></span>
        <span></span>
        <span></span>

    </button>

</header>


<div
    class="overlay"
    id="overlay"
    onclick="closeMenu()"
></div>


<nav
    class="menu"
    id="menu"
>

    <div class="menu-header">

        <div class="menu-title">
            Menu
        </div>

        <button
            class="menu-close"
            onclick="closeMenu()"
        >
            ×
        </button>

    </div>


    <div class="menu-section">
        Navigation
    </div>

    <a href="/">
        Home
    </a>

    <a href="/dashboard">
        Dashboard
    </a>

    <a href="/reviews">
        Reviews
    </a>


    <div class="menu-section">
        Resources
    </div>

    <a href="/documentation">
        Documentation
    </a>

    <a href="/support">
        Support
    </a>


    <div class="menu-section">
        Legal
    </div>

    <a href="/terms">
        Terms
    </a>

    <a href="/privacy">
        Privacy
    </a>

    <a href="/data">
        Data
    </a>

    <a href="/cookies">
        Cookies
    </a>


    <div class="menu-section">
        Account
    </div>


    {% if user %}

        <a href="/dashboard">
            Dashboard
        </a>

        <a href="/logout">
            Logout
        </a>

    {% else %}

        <a
            href="/login"
            class="discord-login"
        >

            <svg
                class="discord-icon"
                viewBox="0 0 24 24"
                fill="currentColor"
                xmlns="http://www.w3.org/2000/svg"
            >

                <path d="
                    M19.54 5.32
                    A16.7 16.7 0 0 0 15.4 4
                    l-.5 1.02
                    a15.1 15.1 0 0 0-5.8 0
                    L8.6 4
                    a16.7 16.7 0 0 0-4.14 1.32
                    C1.84 9.2 1.13 13 1.48 16.74
                    A16.8 16.8 0 0 0 6.57 19
                    l1.22-1.65
                    c-.67-.24-1.3-.55-1.9-.9
                    l.46-.35
                    c3.66 1.7 7.64 1.7 11.25 0
                    l.47.35
                    c-.6.36-1.23.66-1.9.9
                    L17.4 19
                    a16.8 16.8 0 0 0 5.1-2.26
                    c.4-4.34-.68-8.1-2.96-11.42ZM8.5 14.9
                    c-1.1 0-2-.99-2-2.2
                    0-1.22.88-2.2 2-2.2
                    1.13 0 2.01.99 2 2.2
                    0 1.21-.88 2.2-2 2.2Zm7 0
                    c-1.1 0-2-.99-2-2.2
                    0-1.22.88-2.2 2-2.2
                    1.13 0 2.01.99 2 2.2
                    0 1.21-.88 2.2-2 2.2Z
                "/>

            </svg>

            Login with Discord

        </a>

    {% endif %}

</nav>

"""


# =========================================================
# FOOTER
# =========================================================

FOOTER = """

<footer>

    <div>
        © 2026 Misuki. All rights reserved.
    </div>

    <div class="footer-links">

        <a href="/terms">
            Terms
        </a>

        <a href="/privacy">
            Privacy
        </a>

        <a href="/data">
            Data
        </a>

        <a href="/cookies">
            Cookies
        </a>

    </div>

</footer>

"""


# =========================================================
# COOKIE BANNER
# =========================================================

COOKIE_BANNER = """

<div
    class="cookie"
    id="cookieBanner"
    style="display:none;"
>

    <h3>
        🍪 We use cookies
    </h3>

    <p>
        We use essential cookies to keep your session
        working and optional cookies to improve your
        experience. You can choose which cookies to allow.
    </p>


    <div class="cookie-buttons">

        <button
            class="accept"
            onclick="setCookies('all')"
        >
            Accept All
        </button>


        <button
            class="essential"
            onclick="setCookies('essential')"
        >
            Accept Essential
        </button>


        <button
            class="deny"
            onclick="setCookies('deny')"
        >
            Deny
        </button>

    </div>

</div>


<script>

function setCookies(value) {

    localStorage.setItem(
        "misuki_cookie_consent",
        value
    );

    document.getElementById(
        "cookieBanner"
    ).style.display = "none";

}


if (
    !localStorage.getItem(
        "misuki_cookie_consent"
    )
) {

    document.getElementById(
        "cookieBanner"
    ).style.display = "block";

}


function openMenu() {

    document
        .getElementById("menu")
        .classList.add("open");

    document
        .getElementById("overlay")
        .classList.add("show");

}


function closeMenu() {

    document
        .getElementById("menu")
        .classList.remove("open");

    document
        .getElementById("overlay")
        .classList.remove("show");

}


document.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Escape"
        ) {

            closeMenu();

        }

    }
);

</script>

"""


# =========================================================
# LOGIN
# =========================================================

@app.route("/login")
def login():

    if not CLIENT_ID:

        return (
            "DISCORD_CLIENT_ID is missing.",
            500
        )


    if not CLIENT_SECRET:

        return (
            "DISCORD_CLIENT_SECRET is missing.",
            500
        )


    if not DISCORD_LOGIN_REDIRECT_URI:

        return (
            "DISCORD_LOGIN_REDIRECT_URI is missing.",
            500
        )


    next_url = request.args.get(
        "next"
    )


    if (
        next_url
        and next_url.startswith("/")
        and not next_url.startswith("//")
    ):

        session[
            "next_url"
        ] = next_url

    else:

        session[
            "next_url"
        ] = "/dashboard"


    from urllib.parse import urlencode


    params = {

        "client_id":
            CLIENT_ID,

        "response_type":
            "code",

        "redirect_uri":
            DISCORD_LOGIN_REDIRECT_URI,

        "scope":
            "identify guilds"

    }


    discord_url = (

        "https://discord.com/oauth2/authorize?"

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

        return render_page(

            """

            <section class="section">

                <div class="container">

                    <div class="card">

                        <h1>
                            ❌ OAuth2 Error
                        </h1>

                        <p>
                            Discord returned:
                            {{ error }}
                        </p>

                        <a
                            href="/"
                            class="button manage"
                        >
                            Return Home
                        </a>

                    </div>

                </div>

            </section>

            """,

            error=error

        ), 400


    code = request.args.get(
        "code"
    )


    if not code:

        return (

            """

            <h1>
                ❌ OAuth2 Error
            </h1>

            <p>
                No authorization code was received.
            </p>

            """,

            400

        )


    if not CLIENT_SECRET:

        return (
            "DISCORD_CLIENT_SECRET is missing.",
            500
        )


    if not DISCORD_LOGIN_REDIRECT_URI:

        return (
            "DISCORD_LOGIN_REDIRECT_URI is missing.",
            500
        )


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
            DISCORD_LOGIN_REDIRECT_URI

    }


    try:

        response = requests.post(

            f"{DISCORD_API}/oauth2/token",

            data=token_data,

            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded"
            },

            timeout=10

        )

    except Exception as error:

        return render_page(

            """

            <section class="section">

                <div class="container">

                    <div class="card">

                        <h1>
                            ❌ OAuth2 Error
                        </h1>

                        <p>
                            Could not contact Discord.
                        </p>

                        <p>
                            {{ error }}
                        </p>

                    </div>

                </div>

            </section>

            """,

            error=str(error)

        ), 500


    if response.status_code != 200:

        print(
            "❌ LOGIN token exchange failed:"
        )

        print(
            response.text
        )


        return render_page(

            """

            <section class="section">

                <div class="container">

                    <div class="card">

                        <h1>
                            ❌ OAuth2 Error
                        </h1>

                        <p>
                            Failed to exchange
                            authorization code.
                        </p>

                        <pre>{{ response }}</pre>

                    </div>

                </div>

            </section>

            """,

            response=response.text

        ), 400


    token_json = response.json()


    access_token = token_json.get(
        "access_token"
    )


    if not access_token:

        return (

            "❌ Discord did not return an access token.",

            400

        )


    # -----------------------------------------------------
    # VERIFY USER
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

    except Exception as error:

        return (

            f"❌ Failed to retrieve Discord user: {error}",

            500

        )


    if user_response.status_code != 200:

        return (

            "❌ Failed to retrieve Discord user.",

            400

        )


    user = user_response.json()


    # -----------------------------------------------------
    # SAVE NEXT URL BEFORE SESSION RESET
    # -----------------------------------------------------

    next_url = session.get(
        "next_url",
        "/dashboard"
    )


    if (

        not next_url.startswith("/")

        or

        next_url.startswith("//")

    ):

        next_url = "/dashboard"


    # -----------------------------------------------------
    # RESET OLD SESSION
    # -----------------------------------------------------

    session.clear()


    # -----------------------------------------------------
    # CREATE NEW SESSION
    # -----------------------------------------------------

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

    session.modified = True


    print(
        "=========================================="
    )

    print(
        "✅ DISCORD LOGIN SUCCESSFUL"
    )

    print(
        f"👤 User: {user.get('username')}"
    )

    print(
        f"🆔 ID: {user.get('id')}"
    )

    print(
        f"➡️ Next: {next_url}"
    )

    print(
        "=========================================="
    )


    return redirect(
        next_url
    )


# =========================================================
# SEPARATE /callback
# =========================================================

@app.route("/callback")
def callback():

    """
    This endpoint is intentionally separate
    from Discord login.

    It belongs to the normal OAuth2/add-bot flow.
    """

    error = request.args.get(
        "error"
    )


    if error:

        return render_page(

            """

            <section class="section">

                <div class="container">

                    <div class="card">

                        <h1>
                            ❌ OAuth2 Error
                        </h1>

                        <p>
                            Discord returned:
                            {{ error }}
                        </p>

                        <a
                            href="/"
                            class="button manage"
                        >
                            Return Home
                        </a>

                    </div>

                </div>

            </section>

            """,

            error=error

        ), 400


    code = request.args.get(
        "code"
    )


    if not code:

        return (

            """

            <h1>
                ❌ OAuth2 Error
            </h1>

            <p>
                No authorization code was received.
            </p>

            """,

            400

        )


    if not CLIENT_SECRET:

        return (
            "DISCORD_CLIENT_SECRET is missing.",
            500
        )


    if not DISCORD_REDIRECT_URI:

        return (
            "DISCORD_REDIRECT_URI is missing.",
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
            DISCORD_REDIRECT_URI

    }


    try:

        response = requests.post(

            f"{DISCORD_API}/oauth2/token",

            data=token_data,

            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded"
            },

            timeout=10

        )

    except Exception as error:

        return (

            f"❌ OAuth2 request failed: {error}",

            500

        )


    if response.status_code != 200:

        print(
            "❌ OAuth2 callback failed:"
        )

        print(
            response.text
        )


        return (

            "<h1>❌ OAuth2 Error</h1>"
            "<p>Failed to exchange "
            "authorization code.</p>",

            400

        )


    token_json = response.json()


    return render_page(

        """

        <section class="section">

            <div class="container">

                <div class="card">

                    <h1>
                        ✅ OAuth2 Authorization
                    </h1>

                    <p>
                        The OAuth2 authorization was
                        successfully completed.
                    </p>

                    <p>
                        You can return to Misuki.
                    </p>

                    <a
                        href="/"
                        class="button manage"
                    >
                        Return Home
                    </a>

                </div>

            </div>

        </section>

        """,

        user=get_user()

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
# HOME
# =========================================================

@app.route("/")
def index():

    user = get_user()

    reviews = get_random_reviews(
        6
    )


    return render_page(

        """

        <section class="hero">

            <div class="container">

                <h1>
                    Welcome to
                    <span>Misuki</span>
                </h1>

                <p>
                    A powerful Discord experience
                    built around your community.
                </p>

                <a
                    href="/dashboard"
                    class="dashboard-button"
                >
                    🚀 Open Dashboard
                </a>

            </div>

        </section>


        <section class="section">

            <div class="container">

                <h2 class="section-title">
                    ⭐ What people think
                </h2>


                {% if reviews %}

                    <div class="review-grid">

                        {% for review in reviews %}

                            <div class="card review-card">

                                <div class="review-user">

                                    {% if review.avatar %}

                                        <img
                                            class="review-avatar"
                                            src="{{ review.avatar }}"
                                        >

                                    {% else %}

                                        <div
                                            class="review-avatar"
                                            style="
                                                background:#5865f2;
                                                display:flex;
                                                align-items:center;
                                                justify-content:center;
                                            "
                                        >
                                            👤
                                        </div>

                                    {% endif %}


                                    <div>

                                        <strong>
                                            {{ review.username }}
                                        </strong>

                                        <div class="stars">

                                            {% for i in range(review.rating) %}

                                                ★

                                            {% endfor %}

                                        </div>

                                    </div>

                                </div>


                                <div class="review-text">

                                    {{ review.review }}

                                </div>

                            </div>

                        {% endfor %}

                    </div>

                {% else %}

                    <div class="empty">
                        No reviews yet.
                    </div>

                {% endif %}

            </div>

        </section>

        """,

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


    print(
        "========== DASHBOARD =========="
    )

    print(
        f"👤 User: {user.get('username')}"
    )

    print(
        f"🔐 Session keys: "
        f"{list(session.keys())}"
    )

    print(
        "================================"
    )


    user_guilds = get_user_guilds()

    bot_guilds = get_bot_guilds()


    bot_guild_ids = {

        str(
            guild.get("id")
        )

        for guild in bot_guilds

    }


    authorized = []

    available = []


    for guild in user_guilds:

        guild_id = str(
            guild.get("id")
        )


        if guild_id in bot_guild_ids:

            authorized.append(
                guild
            )

        else:

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


    available.sort(

        key=lambda guild:
            not guild.get(
                "can_add",
                False
            )

    )


    return render_page(

        """

        <section class="section">

            <div class="container">

                <h1>
                    🎛️ Dashboard
                </h1>


                <p style="color:#aeb3c0;">

                    Logged in as

                    <strong>
                        {{ user.global_name or user.username }}
                    </strong>

                </p>


                <h2
                    class="section-title"
                    style="margin-top:50px;"
                >
                    🔐 Authorized Servers
                </h2>


                {% if authorized %}

                    <div class="server-grid">

                        {% for guild in authorized %}

                            <div class="card server-card">

                                <div class="server-top">

                                    {% if guild.icon %}

                                        <img
                                            class="server-icon"
                                            src="https://cdn.discordapp.com/icons/{{ guild.id }}/{{ guild.icon }}.png?size=128"
                                        >

                                    {% else %}

                                        <div
                                            class="server-icon-placeholder"
                                        >
                                            {{ guild.name[0] }}
                                        </div>

                                    {% endif %}


                                    <div>

                                        <div class="server-name">
                                            {{ guild.name }}
                                        </div>

                                        <div class="server-id">
                                            {{ guild.id }}
                                        </div>

                                    </div>

                                </div>


                                <a
                                    class="button manage"
                                    href="/manage/{{ guild.id }}"
                                >
                                    ⚙️ Manage
                                </a>

                            </div>

                        {% endfor %}

                    </div>

                {% else %}

                    <div class="empty">
                        🔒 No authorized servers found.
                    </div>

                {% endif %}


                <h2
                    class="section-title"
                    style="margin-top:65px;"
                >
                    ➕ Available Servers
                </h2>


                {% if available %}

                    <div class="server-grid">

                        {% for guild in available %}

                            <div class="card server-card">

                                <div class="server-top">

                                    {% if guild.icon %}

                                        <img
                                            class="server-icon"
                                            src="https://cdn.discordapp.com/icons/{{ guild.id }}/{{ guild.icon }}.png?size=128"
                                        >

                                    {% else %}

                                        <div
                                            class="server-icon-placeholder"
                                        >
                                            {{ guild.name[0] }}
                                        </div>

                                    {% endif %}


                                    <div>

                                        <div class="server-name">
                                            {{ guild.name }}
                                        </div>

                                        <div class="server-id">
                                            {{ guild.id }}
                                        </div>

                                    </div>

                                </div>


                                {% if guild.can_add %}

                                    <a
                                        href="{{ guild.invite_url }}"
                                        class="button add"
                                    >
                                        ➕ Add Misuki
                                    </a>

                                {% else %}

                                    <div
                                        class="button blocked"
                                    >
                                        🔒 Cannot Add
                                    </div>

                                {% endif %}

                            </div>

                        {% endfor %}

                    </div>

                {% else %}

                    <div class="empty">
                        No additional servers available.
                    </div>

                {% endif %}


                <div
                    style="
                        margin-top:60px;
                        text-align:center;
                    "
                >

                    <a
                        href="/reviews"
                        class="dashboard-button"
                    >
                        ⭐ Leave a Review
                    </a>

                </div>

            </div>

        </section>

        """,

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

        return render_page(

            """

            <section class="section">

                <div class="container">

                    <div class="card">

                        <h1>
                            ❌ Access denied
                        </h1>

                        <p>
                            You are not a member
                            of this server.
                        </p>

                    </div>

                </div>

            </section>

            """,

            user=user

        ), 403


    bot_guilds = get_bot_guilds()


    bot_guild_ids = {

        str(
            g.get("id")
        )

        for g in bot_guilds

    }


    if str(guild_id) not in bot_guild_ids:

        return redirect(
            "/dashboard"
        )


    license_data = get_license(
        guild_id
    )


    return render_page(

        """

        <section class="section">

            <div class="container">

                <a href="/dashboard">
                    ← Back to Dashboard
                </a>


                <div
                    class="card"
                    style="margin-top:25px;"
                >

                    <div class="server-top">

                        {% if guild.icon %}

                            <img
                                class="server-icon"
                                src="https://cdn.discordapp.com/icons/{{ guild.id }}/{{ guild.icon }}.png?size=128"
                            >

                        {% else %}

                            <div
                                class="server-icon-placeholder"
                            >
                                {{ guild.name[0] }}
                            </div>

                        {% endif %}


                        <div>

                            <h1 style="margin:0;">
                                {{ guild.name }}
                            </h1>

                            <div class="server-id">
                                {{ guild.id }}
                            </div>

                        </div>

                    </div>


                    <h2 style="margin-top:35px;">
                        🔐 License
                    </h2>


                    {% if license_data %}

                        {% set status = license_data[2] %}


                        <p>

                            Status:


                            {% if status == "active" %}

                                <span
                                    class="status-active"
                                >
                                    🟢 Active
                                </span>

                            {% elif status == "expired" %}

                                <span
                                    class="status-expired"
                                >
                                    🔴 Expired
                                </span>

                            {% elif status == "revoked" %}

                                <span
                                    class="status-revoked"
                                >
                                    ⛔ Revoked
                                </span>

                            {% else %}

                                <span>
                                    {{ status }}
                                </span>

                            {% endif %}

                        </p>


                        <p>
                            <strong>
                                License Key
                            </strong>
                        </p>


                        <div class="license-key">

                            {{ license_data[1] }}

                        </div>


                        <p
                            style="margin-top:20px;"
                        >

                            <strong>
                                Expires
                            </strong>

                        </p>


                        {% if license_data[3] %}

                            <p>
                                {{ license_data[3] }}
                            </p>

                        {% else %}

                            <p>
                                Never
                            </p>

                        {% endif %}


                    {% else %}

                        <div class="empty">

                            🔒 This server does not
                            have a Misuki license.

                        </div>

                    {% endif %}

                </div>

            </div>

        </section>

        """,

        user=user,

        guild=guild,

        license_data=license_data

    )


# =========================================================
# REVIEWS
# =========================================================

def get_random_reviews(
    amount=6
):

    try:

        with database_connection() as connection:

            cursor = connection.cursor()

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

        reviews.append(

            {

                "id": row[0],

                "user_id": row[1],

                "username": row[2],

                "avatar": row[3],

                "review": row[4],

                "rating": row[5],

                "created_at": row[6]

            }

        )


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


    return render_page(

        """

        <section class="section">

            <div class="container">

                <h1>
                    ⭐ Misuki Reviews
                </h1>


                <p style="color:#aeb3c0;">

                    Reviews from members of
                    Misuki communities.

                </p>


                {% if can_review %}

                    <div class="card form">

                        <h2>
                            ✍️ Write a review
                        </h2>


                        <form
                            method="POST"
                            action="/reviews"
                        >

                            <label>
                                Rating
                            </label>


                            <select
                                name="rating"
                                required
                            >

                                <option value="5">
                                    5 — ⭐⭐⭐⭐⭐
                                </option>

                                <option value="4">
                                    4 — ⭐⭐⭐⭐
                                </option>

                                <option value="3">
                                    3 — ⭐⭐⭐
                                </option>

                                <option value="2">
                                    2 — ⭐⭐
                                </option>

                                <option value="1">
                                    1 — ⭐
                                </option>

                            </select>


                            <label>
                                Review
                            </label>


                            <textarea
                                name="review"
                                maxlength="1000"
                                required
                                placeholder="Tell us what you think about Misuki..."
                            ></textarea>


                            <button
                                class="button manage"
                                type="submit"
                            >
                                ⭐ Submit Review
                            </button>

                        </form>

                    </div>


                {% elif user %}

                    <div class="empty">

                        🔒 You need an active Misuki
                        license to write a review.

                    </div>


                {% else %}

                    <div class="empty">

                        🔐 Log in with Discord and have
                        an active Misuki license to
                        write a review.

                    </div>

                {% endif %}


                <h2
                    class="section-title"
                    style="margin-top:60px;"
                >
                    💬 Community Reviews
                </h2>


                {% if review_list %}

                    <div class="review-grid">

                        {% for review in review_list %}

                            <div class="card review-card">

                                <div class="review-user">

                                    {% if review.avatar %}

                                        <img
                                            class="review-avatar"
                                            src="{{ review.avatar }}"
                                        >

                                    {% else %}

                                        <div
                                            class="review-avatar"
                                            style="
                                                background:#5865f2;
                                                display:flex;
                                                align-items:center;
                                                justify-content:center;
                                            "
                                        >
                                            👤
                                        </div>

                                    {% endif %}


                                    <div>

                                        <strong>
                                            {{ review.username }}
                                        </strong>


                                        <div class="stars">

                                            {% for i in range(review.rating) %}

                                                ★

                                            {% endfor %}

                                        </div>

                                    </div>

                                </div>


                                <div class="review-text">

                                    {{ review.review }}

                                </div>

                            </div>

                        {% endfor %}

                    </div>

                {% else %}

                    <div class="empty">
                        No reviews yet.
                    </div>

                {% endif %}

            </div>

        </section>

        """,

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

        return render_page(

            """

            <section class="section">

                <div class="container">

                    <div class="card">

                        <h1>
                            🔒 License required
                        </h1>

                        <p>
                            Only users with an active
                            Misuki license can submit
                            reviews.
                        </p>


                        <a
                            href="/reviews"
                            class="button manage"
                        >
                            Back to Reviews
                        </a>

                    </div>

                </div>

            </section>

            """,

            user=user

        ), 403


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

    except ValueError:

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


    with database_connection() as connection:

        connection.execute(

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

            VALUES (?, ?, ?, ?, ?, ?)

            """,

            (

                user_id,

                username,

                avatar,

                review,

                rating,

                datetime.now().isoformat()

            )

        )

        connection.commit()


    return redirect(
        "/reviews"
    )


# =========================================================
# DOCUMENTATION
# =========================================================

@app.route("/documentation")
def documentation():

    return render_page(

        """

        <section class="section">

            <div class="container">

                <div class="card">

                    <h1>
                        Documentation
                    </h1>

                    <p>
                        Learn how to configure and use
                        Misuki in your Discord server.
                    </p>

                    <p>
                        More documentation will be
                        available here soon.
                    </p>

                </div>

            </div>

        </section>

        """

    )


# =========================================================
# SUPPORT
# =========================================================

@app.route("/support")
def support():

    return render_page(

        """

        <section class="section">

            <div class="container">

                <div class="card">

                    <h1>
                        Support
                    </h1>

                    <p>
                        Need help with Misuki?
                    </p>

                    <p>
                        Contact the Misuki support team
                        through the official support channels.
                    </p>

                </div>

            </div>

        </section>

        """

    )


# =========================================================
# TERMS
# =========================================================

@app.route("/terms")
def terms():

    return render_page(

        """

        <section class="section">

            <div class="container">

                <div class="card">

                    <h1>
                        📄 Terms of Service
                    </h1>

                    <p>
                        By using Misuki, you agree to use
                        the service responsibly and in
                        accordance with applicable rules
                        and Discord's policies.
                    </p>

                    <p>
                        Misuki may restrict or terminate
                        access to services when necessary.
                    </p>

                </div>

            </div>

        </section>

        """

    )


# =========================================================
# PRIVACY
# =========================================================

@app.route("/privacy")
def privacy():

    return render_page(

        """

        <section class="section">

            <div class="container">

                <div class="card">

                    <h1>
                        🔐 Privacy Policy
                    </h1>

                    <p>
                        Misuki uses Discord OAuth2 to
                        authenticate users and obtain the
                        Discord information required for
                        the dashboard.
                    </p>

                    <p>
                        We do not request your Discord
                        password.
                    </p>

                    <p>
                        Information is only used for the
                        functionality of the Misuki service.
                    </p>

                </div>

            </div>

        </section>

        """

    )


# =========================================================
# DATA
# =========================================================

@app.route("/data")
def data_page():

    return render_page(

        """

        <section class="section">

            <div class="container">

                <div class="card">

                    <h1>
                        🗄️ Data
                    </h1>

                    <p>
                        Misuki stores information required
                        for authentication, server management,
                        licenses and reviews.
                    </p>

                    <p>
                        You can contact the Misuki
                        administrator regarding data
                        questions or deletion requests.
                    </p>

                </div>

            </div>

        </section>

        """

    )


# =========================================================
# COOKIES
# =========================================================

@app.route("/cookies")
def cookies_page():

    return render_page(

        """

        <section class="section">

            <div class="container">

                <div class="card">

                    <h1>
                        🍪 Cookies
                    </h1>

                    <p>
                        Misuki uses essential cookies to
                        maintain authentication sessions.
                    </p>

                    <p>
                        Cookie preferences are stored
                        locally in your browser.
                    </p>

                    <p>
                        You can change your preference
                        by clearing the site's local
                        storage.
                    </p>

                </div>

            </div>

        </section>

        """

    )


# =========================================================
# RENDER
# =========================================================

def render_page(
    content,
    **context
):

    if "user" not in context:

        context[
            "user"
        ] = get_user()


    html = f"""

<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>
        Misuki
    </title>

    {BASE_STYLE}

</head>


<body>

    {render_template_string(
        HEADER,
        **context
    )}


    {render_template_string(
        content,
        **context
    )}


    {FOOTER}


    {COOKIE_BANNER}

</body>

</html>

"""


    return render_template_string(
        html,
        **context
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    port = int(
        os.getenv(
            "PORT",
            "5000"
        )
    )


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
        f"🌐 Port: {port}"
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
        f"🔗 OAuth2 Redirect: "
        f"{DISCORD_REDIRECT_URI}"
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
        "=========================================="
    )


    app.run(

        host="0.0.0.0",

        port=port,

        debug=False

    )

