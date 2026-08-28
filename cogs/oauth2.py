
# =========================================================
# MISUKI OAUTH2 — LOGIN + DASHBOARD
# =========================================================

import os
import secrets

import requests

from flask import (
    Flask,
    redirect,
    session,
    url_for,
    request
)

from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv(
    os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        ".env"
    )
)


# =========================================================
# CONFIG
# =========================================================

CLIENT_ID = os.getenv(
    "DISCORD_CLIENT_ID"
)

CLIENT_SECRET = os.getenv(
    "DISCORD_CLIENT_SECRET"
)

REDIRECT_URI = os.getenv(
    "DISCORD_REDIRECT_URI"
)

BOT_TOKEN = os.getenv(
    "DISCORD_TOKEN"
)

# Secret usado pelo Flask para proteger a sessão.
# Se existir no .env, usa-o.
# Caso contrário, cria um temporário.
FLASK_SECRET = os.getenv(
    "FLASK_SECRET"
)

if not FLASK_SECRET:

    FLASK_SECRET = secrets.token_hex(32)


# =========================================================
# DISCORD API
# =========================================================

DISCORD_API = (
    "https://discord.com/api/v10"
)


# =========================================================
# FLASK
# =========================================================

app = Flask(
    __name__
)

app.secret_key = FLASK_SECRET


# =========================================================
# HELPERS
# =========================================================

def get_user_guilds(
    access_token
):

    response = requests.get(
        f"{DISCORD_API}/users/@me/guilds",
        headers={
            "Authorization":
            f"Bearer {access_token}"
        },
        timeout=15
    )

    if response.status_code != 200:

        print(
            "❌ Failed to get user guilds:",
            response.status_code,
            response.text
        )

        return []

    return response.json()


def get_bot_guilds():

    if not BOT_TOKEN:

        print(
            "❌ DISCORD_TOKEN is not configured."
        )

        return []

    response = requests.get(
        f"{DISCORD_API}/users/@me/guilds",
        headers={
            "Authorization":
            f"Bot {BOT_TOKEN}"
        },
        timeout=15
    )

    if response.status_code != 200:

        print(
            "❌ Failed to get bot guilds:",
            response.status_code,
            response.text
        )

        return []

    return response.json()


def can_manage_guild(
    guild
):

    permissions = int(
        guild.get(
            "permissions",
            0
        )
    )

    # MANAGE_GUILD = 0x20
    # ADMINISTRATOR = 0x8

    return bool(
        permissions & 0x20
        or
        permissions & 0x8
    )


def get_guild_icon(
    guild
):

    icon = guild.get(
        "icon"
    )

    guild_id = guild.get(
        "id"
    )

    if not icon:

        return (
            "https://cdn.discordapp.com/"
            "embed/avatars/0.png"
        )

    return (
        f"https://cdn.discordapp.com/"
        f"icons/{guild_id}/{icon}.png"
    )


def get_bot_invite_url(
    guild_id
):

    return (
        "https://discord.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&permissions=0"
        f"&scope=bot%20applications.commands"
        f"&guild_id={guild_id}"
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "access_token" in session:

        return redirect(
            url_for(
                "dashboard"
            )
        )

    return """
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>Misuki</title>

        <style>

            body {
                margin: 0;
                background: #0f1117;
                color: white;
                font-family: Arial, sans-serif;

                display: flex;
                align-items: center;
                justify-content: center;

                min-height: 100vh;
            }

            .container {
                text-align: center;
                max-width: 600px;
                padding: 40px;
            }

            h1 {
                font-size: 48px;
                margin-bottom: 10px;
            }

            p {
                color: #aeb4c0;
                font-size: 18px;
                margin-bottom: 30px;
            }

            .login {
                display: inline-block;
                padding: 14px 28px;

                background: #5865f2;
                color: white;

                text-decoration: none;

                border-radius: 8px;

                font-weight: bold;
                font-size: 16px;
            }

            .login:hover {
                background: #4752c4;
            }

        </style>

    </head>

    <body>

        <div class="container">

            <h1>🌸 Misuki</h1>

            <p>
                Manage your Discord servers
                with Misuki.
            </p>

            <a
                class="login"
                href="/login"
            >
                Login with Discord
            </a>

        </div>

    </body>

    </html>
    """


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login"
)
def login():

    params = {

        "client_id":
            CLIENT_ID,

        "response_type":
            "code",

        "redirect_uri":
            REDIRECT_URI,

        "scope":
            "identify guilds"
    }

    discord_url = (
        "https://discord.com/oauth2/authorize?"
        + requests.compat.urlencode(
            params
        )
    )

    return redirect(
        discord_url
    )


# =========================================================
# CALLBACK
# =========================================================

@app.route(
    "/callback"
)
def callback():

    print(
        "========================================"
    )

    print(
        "🔥 CALLBACK RECEIVED"
    )

    print(
        "========================================"
    )

    code = request.args.get(
        "code"
    )

    error = request.args.get(
        "error"
    )

    if error:

        print(
            "❌ Discord OAuth error:",
            error
        )

        return (
            "<h1>❌ OAuth2 Error</h1>"
            "<p>Discord authorization was denied.</p>"
        ), 400

    if not code:

        print(
            "❌ No authorization code received."
        )

        return (
            "<h1>❌ OAuth2 Error</h1>"
            "<p>No authorization code was received.</p>"
        ), 400

    print(
        "✅ Authorization code received."
    )

    # -----------------------------------------------------
    # TOKEN
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
            REDIRECT_URI
    }

    print(
        "🔄 Exchanging authorization code..."
    )

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

    except Exception as exc:

        print(
            "❌ Token request failed:",
            exc
        )

        return (
            "<h1>❌ OAuth2 Error</h1>"
            "<p>Failed to contact Discord.</p>"
        ), 500

    print(
        "🔑 Token response:",
        response.status_code
    )

    if response.status_code != 200:

        print(
            "❌ Discord token error:",
            response.text
        )

        return (
            "<h1>❌ OAuth2 Error</h1>"
            "<p>Failed to exchange authorization code.</p>"
        ), 400

    token = response.json()

    access_token = token.get(
        "access_token"
    )

    if not access_token:

        print(
            "❌ No access token received."
        )

        return (
            "<h1>❌ OAuth2 Error</h1>"
            "<p>No access token received.</p>"
        ), 400

    print(
        "✅ Access token received."
    )

    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------

    user_response = requests.get(
        f"{DISCORD_API}/users/@me",

        headers={
            "Authorization":
                f"Bearer {access_token}"
        },

        timeout=15
    )

    if user_response.status_code != 200:

        print(
            "❌ Failed to get user:",
            user_response.status_code
        )

        return (
            "<h1>❌ OAuth2 Error</h1>"
            "<p>Failed to retrieve Discord user.</p>"
        ), 400

    user = user_response.json()

    print(
        "👤 Logged in as:",
        user.get(
            "username"
        )
    )

    # -----------------------------------------------------
    # SESSION
    # -----------------------------------------------------

    session.clear()

    session[
        "access_token"
    ] = access_token

    session[
        "user"
    ] = user

    print(
        "💾 Session created."
    )

    return redirect(
        url_for(
            "dashboard"
        )
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route(
    "/dashboard"
)
def dashboard():

    access_token = session.get(
        "access_token"
    )

    if not access_token:

        return redirect(
            url_for(
                "login"
            )
        )

    user = session.get(
        "user",
        {}
    )

    # -----------------------------------------------------
    # USER SERVERS
    # -----------------------------------------------------

    user_guilds = get_user_guilds(
        access_token
    )

    # -----------------------------------------------------
    # BOT SERVERS
    # -----------------------------------------------------

    bot_guilds = get_bot_guilds()

    bot_guild_ids = {
        str(
            guild.get("id")
        )
        for guild in bot_guilds
    }

    # -----------------------------------------------------
    # SEPARATE SERVERS
    # -----------------------------------------------------

    authorized_servers = []

    available_servers = []

    blocked_servers = []

    for guild in user_guilds:

        guild_id = str(
            guild.get(
                "id"
            )
        )

        server = {

            "id":
                guild_id,

            "name":
                guild.get(
                    "name",
                    "Unknown Server"
                ),

            "icon":
                get_guild_icon(
                    guild
                ),

            "manageable":
                can_manage_guild(
                    guild
                )
        }

        # -------------------------------------------------
        # BOT ALREADY THERE
        # -------------------------------------------------

        if guild_id in bot_guild_ids:

            authorized_servers.append(
                server
            )

        # -------------------------------------------------
        # BOT NOT THERE
        # -------------------------------------------------

        elif server["manageable"]:

            available_servers.append(
                server
            )

        # -------------------------------------------------
        # USER CANNOT ADD BOT
        # -------------------------------------------------

        else:

            blocked_servers.append(
                server
            )

    # -----------------------------------------------------
    # HTML
    # -----------------------------------------------------

    html = """

    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>Misuki Dashboard</title>

        <style>

            * {
                box-sizing: border-box;
            }

            body {

                margin: 0;

                background:
                    #0f1117;

                color:
                    #ffffff;

                font-family:
                    Arial,
                    sans-serif;
            }

            .navbar {

                height: 70px;

                display: flex;

                align-items: center;

                justify-content:
                    space-between;

                padding:
                    0 30px;

                background:
                    #151821;

                border-bottom:
                    1px solid #242936;
            }

            .brand {

                font-size:
                    22px;

                font-weight:
                    bold;
            }

            .user {

                display: flex;

                align-items:
                    center;

                gap:
                    10px;

                color:
                    #c8ccd6;
            }

            .user img {

                width:
                    38px;

                height:
                    38px;

                border-radius:
                    50%;
            }

            .container {

                max-width:
                    1100px;

                margin:
                    auto;

                padding:
                    40px 20px;
            }

            h1 {

                margin-bottom:
                    8px;

                font-size:
                    32px;
            }

            .subtitle {

                color:
                    #8f96a5;

                margin-bottom:
                    35px;
            }

            .section {

                margin-top:
                    40px;
            }

            .section-title {

                font-size:
                    22px;

                margin-bottom:
                    15px;
            }

            .servers {

                display:
                    grid;

                grid-template-columns:
                    repeat(
                        auto-fill,
                        minmax(
                            280px,
                            1fr
                        )
                    );

                gap:
                    15px;
            }

            .server {

                background:
                    #181b24;

                border:
                    1px solid #292e3a;

                border-radius:
                    12px;

                padding:
                    18px;

                display:
                    flex;

                align-items:
                    center;

                gap:
                    15px;
            }

            .server.blocked {

                opacity:
                    0.45;
            }

            .icon {

                width:
                    52px;

                height:
                    52px;

                border-radius:
                    50%;

                flex-shrink:
                    0;
            }

            .info {

                min-width:
                    0;

                flex:
                    1;
            }

            .name {

                font-weight:
                    bold;

                white-space:
                    nowrap;

                overflow:
                    hidden;

                text-overflow:
                    ellipsis;
            }

            .status {

                font-size:
                    13px;

                color:
                    #8f96a5;

                margin-top:
                    5px;
            }

            .button {

                padding:
                    9px 14px;

                border-radius:
                    7px;

                text-decoration:
                    none;

                font-size:
                    13px;

                font-weight:
                    bold;

                white-space:
                    nowrap;
            }

            .manage {

                background:
                    #5865f2;

                color:
                    white;
            }

            .add {

                background:
                    #23a55a;

                color:
                    white;
            }

            .disabled {

                background:
                    #30343d;

                color:
                    #777e8b;

                cursor:
                    not-allowed;
            }

            .empty {

                padding:
                    25px;

                border:
                    1px dashed #303542;

                border-radius:
                    10px;

                color:
                    #777e8b;

                text-align:
                    center;
            }

        </style>

    </head>

    <body>

        <div class="navbar">

            <div class="brand">
                🌸 Misuki
            </div>

            <div class="user">
    """

    # -----------------------------------------------------
    # USER AVATAR
    # -----------------------------------------------------

    user_id = user.get(
        "id"
    )

    avatar = user.get(
        "avatar"
    )

    if avatar:

        user_avatar = (
            f"https://cdn.discordapp.com/"
            f"avatars/{user_id}/{avatar}.png"
        )

    else:

        user_avatar = (
            "https://cdn.discordapp.com/"
            "embed/avatars/0.png"
        )

    username = user.get(
        "username",
        "Discord User"
    )

    html += f"""
                <img
                    src="{user_avatar}"
                    alt="Avatar"
                >

                <span>
                    {username}
                </span>

            </div>

        </div>

        <div class="container">

            <h1>
                Dashboard
            </h1>

            <div class="subtitle">
                Manage your Discord servers
                with Misuki.
            </div>

            <!-- =========================================
                 AUTHORIZED SERVERS
                 ========================================= -->

            <div class="section">

                <div class="section-title">
                    🟢 Authorized Servers
                </div>

                <div class="servers">
    """

    if authorized_servers:

        for server in authorized_servers:

            html += f"""
                    <div class="server">

                        <img
                            class="icon"
                            src="{server['icon']}"
                        >

                        <div class="info">

                            <div class="name">
                                {server['name']}
                            </div>

                            <div class="status">
                                Misuki is installed
                            </div>

                        </div>

                        <a
                            class="button manage"
                            href="/server/{server['id']}"
                        >
                            Manage
                        </a>

                    </div>
            """

    else:

        html += """
                    <div class="empty">
                        No authorized servers.
                    </div>
        """

    html += """

                </div>

            </div>

            <!-- =========================================
                 AVAILABLE SERVERS
                 ========================================= -->

            <div class="section">

                <div class="section-title">
                    ➕ Available Servers
                </div>

                <div class="servers">
    """

    # -----------------------------------------------------
    # AVAILABLE — FIRST
    # -----------------------------------------------------

    if available_servers:

        for server in available_servers:

            invite_url = get_bot_invite_url(
                server["id"]
            )

            html += f"""
                    <div class="server">

                        <img
                            class="icon"
                            src="{server['icon']}"
                        >

                        <div class="info">

                            <div class="name">
                                {server['name']}
                            </div>

                            <div class="status">
                                Available to add
                            </div>

                        </div>

                        <a
                            class="button add"
                            href="{invite_url}"
                        >
                            Add Misuki
                        </a>

                    </div>
            """

    # -----------------------------------------------------
    # BLOCKED — SECOND
    # -----------------------------------------------------

    if blocked_servers:

        for server in blocked_servers:

            html += f"""
                    <div class="server blocked">

                        <img
                            class="icon"
                            src="{server['icon']}"
                        >

                        <div class="info">

                            <div class="name">
                                {server['name']}
                            </div>

                            <div class="status">
                                You cannot add Misuki
                            </div>

                        </div>

                        <span
                            class="button disabled"
                        >
                            Locked
                        </span>

                    </div>
            """

    if not available_servers and not blocked_servers:

        html += """
                    <div class="empty">
                        No available servers.
                    </div>
        """

    html += """

                </div>

            </div>

        </div>

    </body>

    </html>
    """

    return html


# =========================================================
# SERVER MANAGEMENT
# =========================================================

@app.route(
    "/server/<guild_id>"
)
def server_management(
    guild_id
):

    access_token = session.get(
        "access_token"
    )

    if not access_token:

        return redirect(
            url_for(
                "login"
            )
        )

    # -----------------------------------------------------
    # CHECK USER GUILDS
    # -----------------------------------------------------

    user_guilds = get_user_guilds(
        access_token
    )

    guild = None

    for current_guild in user_guilds:

        if str(
            current_guild.get("id")
        ) == str(guild_id):

            guild = current_guild

            break

    if guild is None:

        return (
            "<h1>❌ Access denied</h1>"
            "<p>You do not have access to this server.</p>"
        ), 403

    # -----------------------------------------------------
    # CHECK BOT
    # -----------------------------------------------------

    bot_guilds = get_bot_guilds()

    installed = any(
        str(
            current_guild.get("id")
        ) == str(guild_id)
        for current_guild in bot_guilds
    )

    if not installed:

        return redirect(
            url_for(
                "dashboard"
            )
        )

    # -----------------------------------------------------
    # PAGE
    # -----------------------------------------------------

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>
            {guild.get("name", "Server")} — Misuki
        </title>

        <style>

            body {{
                margin: 0;
                background: #0f1117;
                color: white;
                font-family: Arial, sans-serif;

                min-height: 100vh;

                display: flex;
                align-items: center;
                justify-content: center;
            }}

            .box {{
                text-align: center;
                background: #181b24;
                border: 1px solid #292e3a;
                border-radius: 14px;
                padding: 40px;
                max-width: 500px;
            }}

            a {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 18px;
                background: #5865f2;
                color: white;
                text-decoration: none;
                border-radius: 7px;
            }}

        </style>

    </head>

    <body>

        <div class="box">

            <h1>
                🌸 {guild.get("name", "Server")}
            </h1>

            <p>
                Misuki is authorized on this server.
            </p>

            <a href="/dashboard">
                ← Back to Dashboard
            </a>

        </div>

    </body>

    </html>
    """


# =========================================================
# LOGOUT
# =========================================================

@app.route(
    "/logout"
)
def logout():

    session.clear()

    return redirect(
        url_for(
            "home"
        )
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    print(
        "🌐 Misuki OAuth2 starting..."
    )

    print(
        f"🔑 Client ID loaded: "
        f"{bool(CLIENT_ID)}"
    )

    print(
        f"🔐 Client Secret loaded: "
        f"{bool(CLIENT_SECRET)}"
    )

    print(
        f"🤖 Bot Token loaded: "
        f"{bool(BOT_TOKEN)}"
    )

    print(
        f"🔗 Redirect URI: "
        f"{REDIRECT_URI}"
    )

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

