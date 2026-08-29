
# =========================================================
# MISUKI - DISCORD API
# =========================================================

import requests


# =========================================================
# CONFIG
# =========================================================

DISCORD_API_URL = "https://discord.com/api"


# =========================================================
# REQUEST HEADERS
# =========================================================

def get_headers(
    access_token
):

    return {
        "Authorization": f"Bearer {access_token}"
    }


# =========================================================
# USER
# =========================================================

def get_user(
    access_token
):

    if not access_token:

        return None

    response = requests.get(
        f"{DISCORD_API_URL}/users/@me",
        headers=get_headers(
            access_token
        ),
        timeout=10
    )

    if response.status_code != 200:

        return None

    return response.json()


# =========================================================
# GUILDS
# =========================================================

def get_guilds(
    access_token
):

    if not access_token:

        return []

    response = requests.get(
        f"{DISCORD_API_URL}/users/@me/guilds",
        headers=get_headers(
            access_token
        ),
        timeout=10
    )

    if response.status_code != 200:

        return []

    return response.json()


# =========================================================
# BOT GUILD
# =========================================================

def get_bot_guilds(
    bot_token
):

    if not bot_token:

        return []

    response = requests.get(
        f"{DISCORD_API_URL}/users/@me/guilds",
        headers={
            "Authorization":
                f"Bot {bot_token}"
        },
        timeout=10
    )

    if response.status_code != 200:

        return []

    return response.json()

