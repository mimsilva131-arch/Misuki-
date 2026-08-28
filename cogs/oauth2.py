
# =========================================================
# MISUKI OAUTH2
# Login + Dashboard + Servers + Licenses + Reviews
# =========================================================

import os
import random
import sqlite3

import requests

from datetime import datetime

from flask import (
    Flask,
    redirect,
    request,
    session,
    url_for,
    render_template_string
)

from dotenv import load_dotenv


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

LOGIN_REDIRECT_URI = os.getenv(
    "DISCORD_LOGIN_REDIRECT_URI"
)

BOT_TOKEN = os.getenv(
    "DISCORD_BOT_TOKEN"
)

SESSION_SECRET = os.getenv(
    "SESSION_SECRET"
)

if not SESSION_SECRET:

    SESSION_SECRET = os.urandom(
        32
    ).hex()


# =========================================================
# DATABASE
# =========================================================

DATABASE = "data/misuki.db"


# =========================================================
# FLASK
# =========================================================

app = Flask(
    __name__
)

app.secret_key = SESSION_SECRET

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Render uses HTTPS.
# Codespaces can use HTTP locally.
app.config["SESSION_COOKIE_SECURE"] = (
    os.getenv(
        "SESSION_COOKIE_SECURE",
        "true"
    ).lower() == "true"
)


# =========================================================
# DISCORD API
# =========================================================

DISCORD_API = (
    "https://discord.com/api"
)

OAUTH_AUTHORIZE = (
    "https://discord.com/oauth2/authorize"
)

OAUTH_TOKEN = (
    "https://discord.com/api/oauth2/token"
)

USER_ENDPOINT = (
    f"{DISCORD_API}/users/@me"
)

GUILDS_ENDPOINT = (
    f"{DISCORD_API}/users/@me/guilds"
)


# =========================================================
# DATABASE SETUP
# =========================================================

def create_database():

    os.makedirs(
        os.path.dirname(DATABASE),
        exist_ok=True
    )

    with sqlite3.connect(
        DATABASE
    ) as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                username TEXT NOT NULL,

                avatar TEXT,

                rating INTEGER NOT NULL,

                review TEXT NOT NULL,

                created_at TEXT NOT NULL

            )
            """
        )

        connection.commit()


create_database()


# =========================================================
# LICENSE DATABASE HELPERS
# =========================================================

def get_license(
    guild_id
):

    with sqlite3.connect(
        DATABASE
    ) as connection:

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


def license_is_active(
    guild_id
):

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

            with sqlite3.connect(
                DATABASE
            ) as connection:

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

            return False

    return True


# =========================================================
# REVIEW PERMISSION
# =========================================================

def user_has_license():

    user_guilds = session.get(
        "guilds",
        []
    )

    for guild in user_guilds:

        try:

            guild_id = int(
                guild["id"]
            )

        except (
            KeyError,
            ValueError,
            TypeError
        ):

            continue

        if license_is_active(
            guild_id
        ):

            return True

    return False


# =========================================================
# DISCORD HELPERS
# =========================================================

def discord_headers(
    token
):

    return {
        "Authorization":
            f"Bearer {token}",

        "Content-Type":
            "application/x-www-form-urlencoded"
    }


def get_discord_user(
    access_token
):

    response = requests.get(
        USER_ENDPOINT,
        headers={
            "Authorization":
                f"Bearer {access_token}"
        },
        timeout=15
    )

    if response.status_code != 200:

        return None

    return response.json()


def get_discord_guilds(
    access_token
):

    response = requests.get(
        GUILDS_ENDPOINT,
        headers={
            "Authorization":
                f"Bearer {access_token}"
        },
        timeout=15
    )

    if response.status_code != 200:

        return []

    return response.json()


def get_bot_guild_ids():

    if not BOT_TOKEN:

        return set()

    response = requests.get(
        f"{DISCORD_API}/users/@me/guilds",
        headers={
            "Authorization":
                f"Bot {BOT_TOKEN}"
        },
        timeout=15
    )

    if response.status_code != 200:

        return set()

    try:

        guilds = response.json()

    except ValueError:

        return set()

    return {
        str(guild["id"])
        for guild in guilds
    }


# =========================================================
# DISCORD PERMISSIONS
# =========================================================

def can_manage_guild(
    guild
):

    try:

        permissions = int(
            guild.get(
                "permissions",
                0
            )
        )

    except (
        ValueError,
        TypeError
    ):

        return False

    # Administrator
    ADMINISTRATOR = 1 << 3

    # Manage Guild
    MANAGE_GUILD = 1 << 5

    return (
        permissions & ADMINISTRATOR
        or
        permissions & MANAGE_GUILD
    )


# =========================================================
# AVATAR
# =========================================================

def avatar_url(
    user
):

    user_id = user.get(
        "id"
    )

    avatar = user.get(
        "avatar"
    )

    if not user_id:

        return (
            "https://cdn.discordapp.com/"
            "embed/avatars/0.png"
        )

    if not avatar:

        return (
            "https://cdn.discordapp.com/"
            f"embed/avatars/"
            f"{int(user_id) % 5}.png"
        )

    return (
        "https://cdn.discordapp.com/"
        f"avatars/{user_id}/{avatar}.png"
    )


# =========================================================
# COMMON CSS
# =========================================================

COMMON_CSS = """

* {
    box-sizing: border-box;
}


html {
    scroll-behavior: smooth;
}


body {

    margin: 0;

    min-height: 100vh;

    background:
        radial-gradient(
            circle at top,
            #171b27 0%,
            #0b0d12 45%,
            #07080b 100%
        );

    color: #f4f5f7;

    font-family:
        Inter,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}


a {
    color: inherit;
}


button {
    font-family: inherit;
}


/* =====================================================
   NAVBAR
   ===================================================== */

.navbar {

    height: 72px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 0 28px;

    border-bottom:
        1px solid rgba(
            255,
            255,
            255,
            .06
        );

    background:
        rgba(
            8,
            10,
            14,
            .72
        );

    backdrop-filter:
        blur(18px);

    position: sticky;

    top: 0;

    z-index: 50;
}


.logo {

    font-size: 21px;

    font-weight: 800;

    letter-spacing: -.5px;

    text-decoration: none;
}


/* =====================================================
   HAMBURGER
   ===================================================== */

.hamburger {

    width: 43px;

    height: 43px;

    display: flex;

    align-items: center;

    justify-content: center;

    border: 1px solid #303541;

    background: #171a21;

    color: white;

    border-radius: 10px;

    cursor: pointer;

    font-size: 22px;
}


.hamburger:hover {

    background: #20242d;
}


.overlay {

    position: fixed;

    inset: 0;

    background:
        rgba(
            0,
            0,
            0,
            .55
        );

    opacity: 0;

    pointer-events: none;

    transition: .2s;

    z-index: 80;
}


.overlay.show {

    opacity: 1;

    pointer-events: auto;
}


.menu {

    position: fixed;

    top: 0;

    right: 0;

    height: 100vh;

    width: 290px;

    background: #101219;

    border-left:
        1px solid #2a2e38;

    transform:
        translateX(100%);

    transition:
        transform .25s ease;

    z-index: 90;

    padding: 20px;
}


.menu.open {

    transform:
        translateX(0);
}


.menu-close {

    display: flex;

    justify-content: flex-end;

    margin-bottom: 24px;
}


.menu-close button {

    width: 38px;

    height: 38px;

    border: 0;

    border-radius: 8px;

    background: #1c2028;

    color: #d7dbe3;

    font-size: 25px;

    cursor: pointer;
}


.menu-item {

    display: flex;

    align-items: center;

    gap: 10px;

    width: 100%;

    padding: 13px 14px;

    margin-bottom: 7px;

    color: #d9dce3;

    text-decoration: none;

    border-radius: 9px;

    transition: .15s;
}


.menu-item:hover {

    background: #1b1f28;

    color: white;
}


.menu-login {

    background: #5865f2;

    color: white;

    margin-bottom: 18px;
}


.menu-login:hover {

    background: #4752c4;

    color: white;
}


/* =====================================================
   DISCORD ICON
   ===================================================== */

.discord-icon {

    width: 20px;

    height: 20px;

    display: flex;

    align-items: center;

    justify-content: center;

    flex-shrink: 0;
}


.discord-icon svg {

    display: block;

    width: 19px;

    height: 19px;

    fill: currentColor;
}


/* =====================================================
   HERO
   ===================================================== */

.hero {

    max-width: 1050px;

    margin: 0 auto;

    padding:
        105px 24px 75px;

    text-align: center;
}


.hero h1 {

    margin: 0;

    font-size:
        clamp(
            40px,
            7vw,
            72px
        );

    line-height: 1;

    letter-spacing: -3px;
}


.hero p {

    max-width: 620px;

    margin:
        24px auto 32px;

    color: #979dab;

    font-size: 17px;

    line-height: 1.65;
}


.dashboard-button {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    min-width: 190px;

    padding: 14px 22px;

    border-radius: 10px;

    background: #5865f2;

    color: white;

    text-decoration: none;

    font-weight: 700;

    transition: .18s;
}


.dashboard-button:hover {

    background: #4752c4;

    transform:
        translateY(-2px);
}


/* =====================================================
   CONTENT
   ===================================================== */

.container {

    width: min(
        1100px,
        calc(100% - 32px)
    );

    margin: 0 auto;

    padding-bottom: 80px;
}


.section {

    margin-bottom: 55px;
}


.section-title {

    margin-bottom: 18px;

    font-size: 25px;

    font-weight: 800;
}


.section-subtitle {

    color: #7f8796;

    margin-top: -10px;

    margin-bottom: 22px;
}


/* =====================================================
   SERVER GRID
   ===================================================== */

.server-grid {

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                280px,
                1fr
            )
        );

    gap: 15px;
}


.server-card {

    padding: 18px;

    background:
        rgba(
            19,
            22,
            29,
            .9
        );

    border:
        1px solid #292e38;

    border-radius: 14px;

    transition:
        border .15s,
        transform .15s;
}


.server-card:hover {

    border-color: #3a414f;

    transform:
        translateY(-2px);
}


.server-card.blocked {

    opacity: .55;

    filter:
        saturate(.45);
}


.server-top {

    display: flex;

    align-items: center;

    gap: 13px;
}


.server-icon {

    width: 48px;

    height: 48px;

    border-radius: 14px;

    object-fit: cover;

    background: #252a34;
}


.server-name {

    font-weight: 750;

    font-size: 15px;

    overflow: hidden;

    text-overflow: ellipsis;

    white-space: nowrap;
}


.server-status {

    margin-top: 4px;

    color: #818897;

    font-size: 12px;
}


.server-actions {

    display: flex;

    gap: 8px;

    margin-top: 17px;
}


.server-button {

    flex: 1;

    padding: 10px 12px;

    border-radius: 8px;

    text-align: center;

    text-decoration: none;

    border: 1px solid #333946;

    background: #1a1e26;

    color: #d9dce4;

    font-size: 13px;

    font-weight: 700;
}


.server-button:hover {

    background: #242934;
}


.server-button.primary {

    background: #5865f2;

    border-color: #5865f2;

    color: white;
}


.server-button.primary:hover {

    background: #4752c4;
}


.server-button.disabled {

    cursor: not-allowed;

    background: #171a20;

    color: #656c79;
}


/* =====================================================
   LICENSE
   ===================================================== */

.license-card {

    padding: 24px;

    border:
        1px solid #2b303a;

    border-radius: 15px;

    background: #13161d;
}


.license-status {

    font-size: 20px;

    font-weight: 800;

    margin-bottom: 20px;
}


.license-row {

    display: flex;

    justify-content: space-between;

    gap: 20px;

    padding: 13px 0;

    border-bottom:
        1px solid #252a33;

    color: #a8afbc;
}


.license-row:last-child {

    border-bottom: 0;
}


.license-value {

    color: white;

    text-align: right;

    word-break: break-word;
}


/* =====================================================
   REVIEWS
   ===================================================== */

.review-grid {

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                280px,
                1fr
            )
        );

    gap: 15px;
}


.review {

    padding: 20px;

    border:
        1px solid #292e38;

    border-radius: 14px;

    background: #13161d;
}


.review-user {

    display: flex;

    align-items: center;

    gap: 10px;

    margin-bottom: 13px;
}


.review-avatar {

    width: 38px;

    height: 38px;

    border-radius: 50%;

    object-fit: cover;
}


.review-name {

    font-weight: 700;

    font-size: 14px;
}


.stars {

    color: #ffc857;

    letter-spacing: 2px;

    font-size: 13px;
}


.review-text {

    color: #aeb4c0;

    line-height: 1.55;

    font-size: 14px;
}


/* =====================================================
   REVIEW FORM
   ===================================================== */

.review-form {

    margin-top: 25px;

    padding: 22px;

    border:
        1px solid #292e38;

    border-radius: 14px;

    background: #11141a;
}


.review-form textarea {

    width: 100%;

    min-height: 120px;

    resize: vertical;

    padding: 12px;

    border:
        1px solid #303641;

    border-radius: 9px;

    background: #0c0f14;

    color: white;

    outline: none;

    font-family: inherit;
}


.review-form select {

    margin:
        10px 0;

    padding: 10px;

    border:
        1px solid #303641;

    border-radius: 8px;

    background: #0c0f14;

    color: white;
}


.review-form button {

    display: block;

    padding: 11px 17px;

    border: 0;

    border-radius: 8px;

    background: #5865f2;

    color: white;

    font-weight: 700;

    cursor: pointer;
}


/* =====================================================
   COOKIE BANNER
   ===================================================== */

.cookie-banner {

    position: fixed;

    bottom: 24px;

    left: 50%;

    transform:
        translateX(-50%);

    width:
        calc(
            100% - 32px
        );

    max-width: 680px;

    padding: 22px;

    background:
        rgba(
            20,
            23,
            31,
            .97
        );

    border:
        1px solid #303642;

    border-radius: 16px;

    z-index: 200;

    box-shadow:
        0 20px 60px
        rgba(
            0,
            0,
            0,
            .45
        );

    backdrop-filter:
        blur(14px);

    transition:
        opacity .25s ease,
        transform .25s ease;
}


.cookie-hidden {

    opacity: 0;

    transform:
        translateX(-50%)
        translateY(20px);
}


.cookie-header {

    display: flex;

    align-items: flex-start;

    gap: 14px;
}


.cookie-icon {

    width: 42px;

    height: 42px;

    flex-shrink: 0;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 10px;

    background: #242936;

    color: #b7becb;
}


.cookie-title {

    color: white;

    font-size: 17px;

    font-weight: 700;

    margin-bottom: 6px;
}


.cookie-description {

    color: #9299a7;

    font-size: 13px;

    line-height: 1.55;
}


.cookie-actions {

    display: flex;

    gap: 9px;

    margin-top: 19px;

    flex-wrap: wrap;
}


.cookie-btn {

    border: 0;

    border-radius: 8px;

    padding: 10px 16px;

    font-size: 13px;

    font-weight: 700;

    cursor: pointer;

    transition:
        background .15s ease,
        transform .15s ease;
}


.cookie-btn:hover {

    transform:
        translateY(-1px);
}


.cookie-accept {

    background: #5865f2;

    color: white;
}


.cookie-accept:hover {

    background: #4752c4;
}


.cookie-essential {

    background: #303642;

    color: #e1e4ea;
}


.cookie-essential:hover {

    background: #3a404d;
}


.cookie-deny {

    background: transparent;

    color: #8e96a5;

    border:
        1px solid #343a47;
}


.cookie-deny:hover {

    background: #20242d;

    color: #c4c9d2;
}


.cookie-bottom {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 12px;

    margin-top: 17px;

    padding-top: 14px;

    border-top:
        1px solid #292e38;

    color: #666e7d;

    font-size: 11px;
}


.cookie-links {

    display: flex;

    align-items: center;

    gap: 7px;

    white-space: nowrap;
}


.cookie-links a {

    color: #8d95a4;

    text-decoration: none;
}


.cookie-links a:hover {

    color: white;

    text-decoration: underline;
}


/* =====================================================
   FOOTER
   ===================================================== */

footer {

    padding:
        30px 20px 45px;

    text-align: center;

    color: #646b78;

    font-size: 12px;
}


footer a {

    color: #858c99;

    text-decoration: none;

    margin: 0 6px;
}


/* =====================================================
   MOBILE
   ===================================================== */

@media (max-width: 600px) {

    .navbar {

        padding:
            0 17px;
    }


    .hero {

        padding:
            80px 18px 55px;
    }


    .hero h1 {

        letter-spacing:
            -2px;
    }


    .container {

        width:
            calc(
                100% - 22px
            );
    }


    .cookie-banner {

        bottom: 12px;

        width:
            calc(
                100% - 20px
            );

        padding: 17px;

        border-radius: 13px;
    }


    .cookie-actions {

        display: grid;

        grid-template-columns:
            1fr 1fr;

        width: 100%;
    }


    .cookie-accept {

        grid-column:
            1 / -1;
    }


    .cookie-btn {

        width: 100%;
    }


    .cookie-bottom {

        align-items: flex-start;

        flex-direction: column;

        gap: 7px;
    }

}
"""


# =========================================================
# HAMBURGER
# =========================================================

def menu_html():

    logged_in = (
        "user" in session
    )

    if logged_in:

        auth = """
        <a
            class="menu-item"
            href="/dashboard"
        >
            Dashboard
        </a>

        <a
            class="menu-item"
            href="/logout"
        >
            Logout
        </a>
        """

    else:

        # Inline SVG.
        # No external image is required.
        auth = """
        <a
            class="menu-item menu-login"
            href="/login"
        >

            <span
                class="discord-icon"
                aria-hidden="true"
            >

                <svg
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                >

                    <path
                        d="M19.54 5.2A16.9 16.9 0 0 0 15.9 4l-.45.92a15.7 15.7 0 0 0-6.9 0L8.1 4a16.9 16.9 0 0 0-3.64 1.2C2.16 8.6 1.54 11.9 1.86 15.15a16.9 16.9 0 0 0 4.48 2.27l1.1-1.5c-.6-.22-1.17-.5-1.7-.82l.42-.32c3.28 1.52 6.83 1.52 10.07 0l.42.32c-.54.32-1.1.6-1.7.82l1.1 1.5a16.9 16.9 0 0 0 4.48-2.27c.37-3.77-.63-7.04-1.99-9.95ZM8.54 13.64c-.98 0-1.78-.9-1.78-2s.78-2 1.78-2c1 0 1.8.9 1.78 2 0 1.1-.79 2-1.78 2Zm6.92 0c-.98 0-1.78-.9-1.78-2s.78-2 1.78-2c1 0 1.8.9 1.78 2 0 1.1-.79 2-1.78 2Z"
                    />

                </svg>

            </span>

            Login with Discord

        </a>
        """

    return f"""

    <button
        class="hamburger"
        onclick="openMenu()"
        aria-label="Open menu"
    >
        ☰
    </button>


    <div
        id="overlay"
        class="overlay"
        onclick="closeMenu()"
    ></div>


    <div
        id="menu"
        class="menu"
    >

        <div class="menu-close">

            <button
                onclick="closeMenu()"
                aria-label="Close menu"
            >
                ×
            </button>

        </div>

        {auth}


        <a
            class="menu-item"
            href="/privacy"
        >
            Privacy
        </a>


        <a
            class="menu-item"
            href="/data"
        >
            Data
        </a>


        <a
            class="menu-item"
            href="/cookies"
        >
            Cookies
        </a>

    </div>


    <script>

    function openMenu() {{

        document
            .getElementById("menu")
            .classList.add("open");

        document
            .getElementById("overlay")
            .classList.add("show");

    }}


    function closeMenu() {{

        document
            .getElementById("menu")
            .classList.remove("open");

        document
            .getElementById("overlay")
            .classList.remove("show");

    }}

    </script>

    """


# =========================================================
# COOKIE BANNER
# =========================================================

def cookie_banner():

    return """

    <div
        id="cookieBanner"
        class="cookie-banner"
    >

        <div class="cookie-header">

            <div class="cookie-icon">

                <svg
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                >

                    <path
                        d="M20.4 13.3A7.7 7.7 0 0 1 10.7 3.6a7.7 7.7 0 1 0 9.7 9.7Z"
                    />

                    <path
                        d="M15 8h.01M18 11h.01M12 14h.01M16 16h.01"
                    />

                </svg>

            </div>


            <div>

                <div class="cookie-title">
                    We value your privacy
                </div>


                <div class="cookie-description">

                    We use cookies to keep Misuki secure,
                    remember your preferences and improve
                    your experience.

                </div>

            </div>

        </div>


        <div class="cookie-actions">

            <button
                class="cookie-btn cookie-accept"
                onclick="acceptAllCookies()"
            >
                Accept all
            </button>


            <button
                class="cookie-btn cookie-essential"
                onclick="acceptEssentialCookies()"
            >
                Accept essential
            </button>


            <button
                class="cookie-btn cookie-deny"
                onclick="denyCookies()"
            >
                Deny
            </button>

        </div>


        <div class="cookie-bottom">

            <span>
                By continuing, you agree to our
            </span>


            <div class="cookie-links">

                <a href="/privacy">
                    Privacy
                </a>

                <span>·</span>

                <a href="/data">
                    Data
                </a>

                <span>·</span>

                <a href="/cookies">
                    Cookies
                </a>

            </div>

        </div>

    </div>


    <script>

    function hideCookieBanner() {{

        const banner =
            document.getElementById(
                "cookieBanner"
            );

        if (banner) {{

            banner.classList.add(
                "cookie-hidden"
            );

            setTimeout(
                function() {{
                    banner.remove();
                }},
                250
            );

        }}

    }}


    function acceptAllCookies() {{

        localStorage.setItem(
            "misuki_cookie_consent",
            "all"
        );

        hideCookieBanner();

    }}


    function acceptEssentialCookies() {{

        localStorage.setItem(
            "misuki_cookie_consent",
            "essential"
        );

        hideCookieBanner();

    }}


    function denyCookies() {{

        localStorage.setItem(
            "misuki_cookie_consent",
            "denied"
        );

        hideCookieBanner();

    }}


    if (
        localStorage.getItem(
            "misuki_cookie_consent"
        )
    ) {{

        const banner =
            document.getElementById(
                "cookieBanner"
            );

        if (banner) {{
            banner.remove();
        }}

    }}

    </script>

    """


# =========================================================
# BASE PAGE
# =========================================================

def page(
    content,
    title="Misuki"
):

    return f"""
    <!DOCTYPE html>

    <html lang="en">

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width,
            initial-scale=1.0"
        >

        <title>
            {title} • Misuki
        </title>

        <style>

            {COMMON_CSS}

        </style>

    </head>


    <body>

        <nav class="navbar">

            <a
                class="logo"
                href="/"
            >
                Misuki
            </a>

            {menu_html()}

        </nav>


        {content}


        <footer>

            <div>
                © 2026 Misuki
            </div>

            <div style="margin-top:8px;">

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


        {cookie_banner()}

    </body>

    </html>
    """


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user" in session:

        dashboard_url = "/dashboard"

        button_text = "Open Dashboard"

    else:

        dashboard_url = "/login"

        button_text = "Login to Dashboard"

    content = f"""

    <main>

        <section class="hero">

            <h1>
                Misuki
            </h1>


            <p>
                Your Discord server management
                experience, all in one place.
            </p>


            <a
                class="dashboard-button"
                href="{dashboard_url}"
            >
                {button_text}
            </a>

        </section>

    </main>

    """

    return page(
        content,
        "Home"
    )


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

    if not LOGIN_REDIRECT_URI:

        return (
            "DISCORD_LOGIN_REDIRECT_URI is missing.",
            500
        )

    authorization_url = (
        f"{OAUTH_AUTHORIZE}"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri="
        f"{requests.utils.quote(LOGIN_REDIRECT_URI, safe='')}"
        f"&scope=identify%20guilds"
    )

    return redirect(
        authorization_url
    )


# =========================================================
# CALLBACK
# =========================================================

@app.route("/callback")
def callback():

    error = request.args.get(
        "error"
    )

    if error:

        return page(
            f"""
            <main class="container">

                <section class="section">

                    <h1>
                        OAuth2 Error
                    </h1>

                    <p>
                        Discord returned:
                        <strong>{error}</strong>
                    </p>

                </section>

            </main>
            """,
            "OAuth2 Error"
        ), 400


    code = request.args.get(
        "code"
    )

    if not code:

        return page(
            """
            <main class="container">

                <section class="section">

                    <h1>
                        OAuth2 Error
                    </h1>

                    <p>
                        No authorization code was received.
                    </p>

                </section>

            </main>
            """,
            "OAuth2 Error"
        ), 400


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


    if not LOGIN_REDIRECT_URI:

        return (
            "DISCORD_LOGIN_REDIRECT_URI is missing.",
            500
        )


    # -----------------------------------------------------
    # EXCHANGE CODE
    # -----------------------------------------------------

    token_response = requests.post(

        OAUTH_TOKEN,

        data={

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

        },

        headers={
            "Content-Type":
                "application/x-www-form-urlencoded"
        },

        timeout=15
    )


    if token_response.status_code != 200:

        return page(
            """
            <main class="container">

                <section class="section">

                    <h1>
                        OAuth2 Error
                    </h1>

                    <p>
                        Failed to exchange
                        authorization code.
                    </p>

                </section>

            </main>
            """,
            "OAuth2 Error"
        ), 400


    token_data = token_response.json()

    access_token = token_data.get(
        "access_token"
    )


    if not access_token:

        return (
            "Discord did not return an access token.",
            400
        )


    # -----------------------------------------------------
    # GET USER
    # -----------------------------------------------------

    user = get_discord_user(
        access_token
    )


    if not user:

        return (
            "Failed to retrieve Discord user.",
            400
        )


    # -----------------------------------------------------
    # GET GUILDS
    # -----------------------------------------------------

    guilds = get_discord_guilds(
        access_token
    )


    # -----------------------------------------------------
    # SAVE SESSION
    # -----------------------------------------------------

    session.clear()

    session["access_token"] = (
        access_token
    )

    session["user"] = user

    session["guilds"] = guilds


    return redirect(
        "/dashboard"
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

    if "user" not in session:

        return redirect(
            "/login"
        )


    user = session["user"]

    guilds = session.get(
        "guilds",
        []
    )


    # -----------------------------------------------------
    # BOT SERVERS
    # -----------------------------------------------------

    bot_guild_ids = (
        get_bot_guild_ids()
    )


    authorized = []

    available = []


    for guild in guilds:

        guild_id = str(
            guild.get(
                "id"
            )
        )

        guild["manageable"] = (
            can_manage_guild(
                guild
            )
        )

        guild["bot_installed"] = (
            guild_id in
            bot_guild_ids
        )

        guild["licensed"] = (
            license_is_active(
                guild_id
            )
        )


        if guild["bot_installed"]:

            authorized.append(
                guild
            )

        else:

            available.append(
                guild
            )


    # -----------------------------------------------------
    # AVAILABLE ORDER
    # -----------------------------------------------------

    # Manageable/addable first.
    # Blocked servers afterwards.

    available.sort(
        key=lambda guild:
            not guild["manageable"]
    )


    # -----------------------------------------------------
    # AUTHORIZED HTML
    # -----------------------------------------------------

    authorized_html = ""


    if authorized:

        for guild in authorized:

            guild_id = guild["id"]

            guild_name = guild.get(
                "name",
                "Unknown Server"
            )

            icon = guild.get(
                "icon"
            )

            if icon:

                icon_url = (
                    "https://cdn.discordapp.com/"
                    f"icons/{guild_id}/"
                    f"{icon}.png"
                )

            else:

                icon_url = (
                    "https://cdn.discordapp.com/"
                    "embed/avatars/0.png"
                )


            if guild["licensed"]:

                status = (
                    "🟢 Active license"
                )

            else:

                status = (
                    "🔴 No active license"
                )


            authorized_html += f"""

            <article class="server-card">

                <div class="server-top">

                    <img
                        class="server-icon"
                        src="{icon_url}"
                        alt=""
                    >


                    <div>

                        <div class="server-name">
                            {guild_name}
                        </div>

                        <div class="server-status">
                            {status}
                        </div>

                    </div>

                </div>


                <div class="server-actions">

                    <a
                        class="server-button primary"
                        href="/server/{guild_id}"
                    >
                        Manage
                    </a>

                </div>

            </article>

            """


    else:

        authorized_html = """

        <div class="license-card">

            <div class="license-status">
                No authorized servers
            </div>

            <div>
                Add Misuki to one of your Discord
                servers to get started.
            </div>

        </div>

        """


    # -----------------------------------------------------
    # AVAILABLE HTML
    # -----------------------------------------------------

    available_html = ""


    for guild in available:

        guild_id = guild["id"]

        guild_name = guild.get(
            "name",
            "Unknown Server"
        )

        icon = guild.get(
            "icon"
        )


        if icon:

            icon_url = (
                "https://cdn.discordapp.com/"
                f"icons/{guild_id}/"
                f"{icon}.png"
            )

        else:

            icon_url = (
                "https://cdn.discordapp.com/"
                "embed/avatars/0.png"
            )


        if guild["manageable"]:

            invite_url = (
                f"{OAUTH_AUTHORIZE}"
                f"?client_id={CLIENT_ID}"
                f"&permissions=0"
                f"&scope=bot%20applications.commands"
                f"&guild_id={guild_id}"
            )


            available_html += f"""

            <article class="server-card">

                <div class="server-top">

                    <img
                        class="server-icon"
                        src="{icon_url}"
                        alt=""
                    >


                    <div>

                        <div class="server-name">
                            {guild_name}
                        </div>

                        <div class="server-status">
                            Ready to add Misuki
                        </div>

                    </div>

                </div>


                <div class="server-actions">

                    <a
                        class="server-button primary"
                        href="{invite_url}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Add Misuki
                    </a>

                </div>

            </article>

            """

        else:

            available_html += f"""

            <article class="server-card blocked">

                <div class="server-top">

                    <img
                        class="server-icon"
                        src="{icon_url}"
                        alt=""
                    >


                    <div>

                        <div class="server-name">
                            {guild_name}
                        </div>

                        <div class="server-status">
                            You cannot manage this server
                        </div>

                    </div>

                </div>


                <div class="server-actions">

                    <span
                        class="server-button disabled"
                    >
                        Unavailable
                    </span>

                </div>

            </article>

            """


    if not available_html:

        available_html = """

        <div class="license-card">

            <div>
                No other servers are available.
            </div>

        </div>

        """


    # -----------------------------------------------------
    # REVIEWS
    # -----------------------------------------------------

    with sqlite3.connect(
        DATABASE
    ) as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                username,
                avatar,
                rating,
                review
            FROM reviews
            """
        )

        reviews = cursor.fetchall()


    random.shuffle(
        reviews
    )


    reviews = reviews[:6]


    reviews_html = ""


    for (
        username,
        avatar,
        rating,
        review
    ) in reviews:

        stars = (
            "★" * rating
            +
            "☆" * (5 - rating)
        )


        reviews_html += f"""

        <article class="review">

            <div class="review-user">

                <img
                    class="review-avatar"
                    src="{avatar}"
                    alt=""
                >


                <div>

                    <div class="review-name">
                        {username}
                    </div>

                    <div class="stars">
                        {stars}
                    </div>

                </div>

            </div>


            <div class="review-text">
                {review}
            </div>

        </article>

        """


    if not reviews_html:

        reviews_html = """

        <div class="license-card">

            <div>
                No reviews yet.
            </div>

        </div>

        """


    # -----------------------------------------------------
    # REVIEW FORM
    # -----------------------------------------------------

    if user_has_license():

        review_form = """

        <div class="review-form">

            <h3>
                Leave a review
            </h3>

            <form
                method="POST"
                action="/review"
            >

                <select
                    name="rating"
                    required
                >

                    <option value="5">
                        5 — Excellent
                    </option>

                    <option value="4">
                        4 — Great
                    </option>

                    <option value="3">
                        3 — Good
                    </option>

                    <option value="2">
                        2 — Fair
                    </option>

                    <option value="1">
                        1 — Poor
                    </option>

                </select>


                <textarea
                    name="review"
                    maxlength="500"
                    placeholder="Tell us what you think about Misuki..."
                    required
                ></textarea>


                <button
                    type="submit"
                >
                    Publish review
                </button>

            </form>

        </div>

        """

    else:

        review_form = """

        <div class="license-card">

            <strong>
                Reviews are available to licensed users.
            </strong>

            <div
                style="
                    margin-top:8px;
                    color:#858c99;
                "
            >
                You need an active Misuki license
                on one of your servers to publish
                a review.
            </div>

        </div>

        """


    # -----------------------------------------------------
    # PAGE
    # -----------------------------------------------------

    content = f"""

    <main class="container">

        <section
            class="hero"
            style="padding-bottom:50px;"
        >

            <h1>
                Dashboard
            </h1>


            <p>
                Welcome back,
                <strong>
                    {user.get("global_name")
                    or user.get("username")
                    or "Discord user"}
                </strong>.
            </p>

        </section>


        <section class="section">

            <div class="section-title">
                Authorized Servers
            </div>

            <div class="section-subtitle">
                Servers where Misuki is installed.
            </div>


            <div class="server-grid">

                {authorized_html}

            </div>

        </section>


        <section class="section">

            <div class="section-title">
                Available Servers
            </div>

            <div class="section-subtitle">
                Add Misuki to one of your manageable
                Discord servers.
            </div>


            <div class="server-grid">

                {available_html}

            </div>

        </section>


        <section class="section">

            <div class="section-title">
                Reviews
            </div>

            <div class="section-subtitle">
                What the Misuki community thinks.
            </div>


            <div class="review-grid">

                {reviews_html}

            </div>


            {review_form}

        </section>

    </main>

    """


    return page(
        content,
        "Dashboard"
    )


# =========================================================
# SERVER MANAGEMENT
# =========================================================

@app.route("/server/<guild_id>")
def server_details(
    guild_id
):

    if "user" not in session:

        return redirect(
            "/login"
        )


    guild = None


    for item in session.get(
        "guilds",
        []
    ):

        if str(
            item.get("id")
        ) == str(
            guild_id
        ):

            guild = item

            break


    if guild is None:

        return (
            "Server not found.",
            404
        )


    bot_guild_ids = (
        get_bot_guild_ids()
    )


    if str(guild_id) not in bot_guild_ids:

        return (
            "Misuki is not installed on this server.",
            400
        )


    if not can_manage_guild(
        guild
    ):

        return (
            "You cannot manage this server.",
            403
        )


    license_data = get_license(
        guild_id
    )


    guild_name = guild.get(
        "name",
        "Unknown Server"
    )


    if license_data:

        (
            db_guild_id,
            license_key,
            status,
            expires_at,
            created_at
        ) = license_data


        if status == "active":

            if expires_at:

                try:

                    expiration = datetime.fromisoformat(
                        expires_at
                    )

                    if datetime.now() >= expiration:

                        status = "expired"

                        with sqlite3.connect(
                            DATABASE
                        ) as connection:

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

                except ValueError:

                    pass


        if status == "active":

            status_text = (
                "🟢 Active"
            )

        elif status == "expired":

            status_text = (
                "🔴 Expired"
            )

        elif status == "revoked":

            status_text = (
                "⛔ Revoked"
            )

        else:

            status_text = (
                f"⚪ {status.title()}"
            )


        if expires_at:

            try:

                expiration = datetime.fromisoformat(
                    expires_at
                )

                expiration_text = (
                    f"<t:{int(expiration.timestamp())}:F>"
                )

            except ValueError:

                expiration_text = expires_at

        else:

            expiration_text = "Never"


        license_html = f"""

        <div class="license-card">

            <div class="license-status">

                {status_text}

            </div>


            <div class="license-row">

                <span>
                    License Key
                </span>

                <span class="license-value">
                    <code>
                        {license_key}
                    </code>
                </span>

            </div>


            <div class="license-row">

                <span>
                    Expires
                </span>

                <span class="license-value">
                    {expiration_text}
                </span>

            </div>


            <div class="license-row">

                <span>
                    Created
                </span>

                <span class="license-value">
                    {created_at}
                </span>

            </div>

        </div>

        """

    else:

        license_html = """

        <div class="license-card">

            <div class="license-status">
                🔴 No license
            </div>

            <div>
                This server does not currently
                have a Misuki license.
            </div>

        </div>

        """


    content = f"""

    <main class="container">

        <section
            class="hero"
            style="padding-bottom:45px;"
        >

            <h1>
                {guild_name}
            </h1>


            <p>
                Server license information.
            </p>

        </section>


        <section class="section">

            <div class="section-title">
                License
            </div>

            {license_html}

        </section>


        <section class="section">

            <a
                href="/dashboard"
                class="server-button"
                style="
                    display:inline-block;
                    width:auto;
                "
            >
                Back to Dashboard
            </a>

        </section>

    </main>

    """


    return page(
        content,
        f"{guild_name} • Misuki"
    )


# =========================================================
# REVIEW
# =========================================================

@app.route(
    "/review",
    methods=["POST"]
)
def submit_review():

    if "user" not in session:

        return redirect(
            "/login"
        )


    if not user_has_license():

        return redirect(
            "/dashboard"
        )


    try:

        rating = int(
            request.form.get(
                "rating",
                5
            )
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


    review = (
        request.form.get(
            "review",
            ""
        )
        .strip()
    )


    if not review:

        return redirect(
            "/dashboard"
        )


    # Maximum 500 characters.
    review = review[:500]


    user = session["user"]


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


    avatar = avatar_url(
        user
    )


    with sqlite3.connect(
        DATABASE
    ) as connection:

        connection.execute(
            """
            INSERT INTO reviews
            (
                user_id,
                username,
                avatar,
                rating,
                review,
                created_at
            )

            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(
                    user["id"]
                ),
                username,
                avatar,
                rating,
                review,
                datetime.now().isoformat()
            )
        )

        connection.commit()


    return redirect(
        "/dashboard"
    )


# =========================================================
# PRIVACY
# =========================================================

@app.route("/privacy")
def privacy():

    content = """

    <main class="container">

        <section class="hero">

            <h1>
                Privacy
            </h1>

            <p>
                Misuki uses Discord OAuth2 to authenticate
                users and display the Discord servers they
                have access to manage.
            </p>

        </section>


        <section class="section">

            <div class="license-card">

                <h2>
                    Information we receive
                </h2>

                <p>
                    When you sign in with Discord, Misuki
                    receives the basic Discord profile and
                    server information permitted by the
                    OAuth2 scopes requested by the application.
                </p>


                <h2>
                    Why we use it
                </h2>

                <p>
                    This information is used to authenticate
                    you, display your servers and determine
                    which servers can be managed through Misuki.
                </p>


                <h2>
                    Reviews
                </h2>

                <p>
                    If you publish a review, your Discord
                    display name and avatar may be shown
                    alongside the review.
                </p>

            </div>

        </section>

    </main>

    """

    return page(
        content,
        "Privacy"
    )


# =========================================================
# DATA
# =========================================================

@app.route("/data")
def data_page():

    content = """

    <main class="container">

        <section class="hero">

            <h1>
                Data
            </h1>

            <p>
                Information about the data used by Misuki.
            </p>

        </section>


        <section class="section">

            <div class="license-card">

                <h2>
                    Discord data
                </h2>

                <p>
                    Misuki uses your Discord account information
                    to provide authentication and dashboard
                    functionality.
                </p>


                <h2>
                    Server data
                </h2>

                <p>
                    Server identifiers and license information
                    are used to determine the status of Misuki
                    on supported servers.
                </p>


                <h2>
                    Reviews
                </h2>

                <p>
                    Reviews are stored in the Misuki database
                    together with the information required to
                    display the author of the review.
                </p>

            </div>

        </section>

    </main>

    """

    return page(
        content,
        "Data"
    )


# =========================================================
# COOKIES
# =========================================================

@app.route("/cookies")
def cookies():

    content = """

    <main class="container">

        <section class="hero">

            <h1>
                Cookies
            </h1>

            <p>
                Information about cookies and local storage
                used by Misuki.
            </p>

        </section>


        <section class="section">

            <div class="license-card">

                <h2>
                    Essential cookies
                </h2>

                <p>
                    Misuki may use essential browser storage
                    to maintain authentication and security.
                </p>


                <h2>
                    Cookie preferences
                </h2>

                <p>
                    Your cookie preference is stored locally
                    in your browser so the consent banner does
                    not appear every time you visit the site.
                </p>


                <h2>
                    Managing preferences
                </h2>

                <p>
                    You can clear your browser's site data to
                    reset your cookie preference.
                </p>

            </div>

        </section>

    </main>

    """

    return page(
        content,
        "Cookies"
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return {
        "status": "ok",
        "oauth2": bool(
            CLIENT_ID
            and CLIENT_SECRET
            and LOGIN_REDIRECT_URI
        )
    }


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    port = int(
        os.getenv(
            "PORT",
            "5000"
        )
    )

    print(
        "========================================"
    )

    print(
        "Misuki OAuth2"
    )

    print(
        "========================================"
    )

    print(
        f"CLIENT_ID: "
        f"{'OK' if CLIENT_ID else 'MISSING'}"
    )

    print(
        f"CLIENT_SECRET: "
        f"{'OK' if CLIENT_SECRET else 'MISSING'}"
    )

    print(
        f"LOGIN_REDIRECT_URI: "
        f"{LOGIN_REDIRECT_URI or 'MISSING'}"
    )

    print(
        f"BOT_TOKEN: "
        f"{'OK' if BOT_TOKEN else 'MISSING'}"
    )

    print(
        f"Database: "
        f"{DATABASE}"
    )

    print(
        f"Port: "
        f"{port}"
    )

    print(
        "========================================"
    )


    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )

