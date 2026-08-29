
# =========================================================
# MISUKI - DISCORD OAUTH2 AUTHENTICATION
# =========================================================

import os

import requests

from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


DISCORD_CLIENT_ID = os.getenv(
    "DISCORD_CLIENT_ID"
)

DISCORD_CLIENT_SECRET = os.getenv(
    "DISCORD_CLIENT_SECRET"
)

DISCORD_LOGIN_REDIRECT_URI = os.getenv(
    "DISCORD_LOGIN_REDIRECT_URI"
)


DISCORD_API_URL = (
    "https://discord.com/api"
)


# =========================================================
# OAUTH2 URL
# =========================================================

def get_discord_login_url():

    return (
        "https://discord.com/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={DISCORD_LOGIN_REDIRECT_URI}"
        "&scope=identify%20guilds"
    )


# =========================================================
# EXCHANGE CODE
# =========================================================

def exchange_code(
    code
):

    if not DISCORD_CLIENT_ID:
        return None

    if not DISCORD_CLIENT_SECRET:
        return None

    if not DISCORD_LOGIN_REDIRECT_URI:
        return None

    response = requests.post(
        f"{DISCORD_API_URL}/oauth2/token",
        data={
            "client_id": DISCORD_CLIENT_ID,
            "client_secret": DISCORD_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": DISCORD_LOGIN_REDIRECT_URI
        },
        headers={
            "Content-Type":
                "application/x-www-form-urlencoded"
        },
        timeout=10
    )

    if response.status_code != 200:

        return None

    return response.json()


# =========================================================
# GET USER
# =========================================================

def get_discord_user(
    access_token
):

    if not access_token:

        return None

    response = requests.get(
        f"{DISCORD_API_URL}/users/@me",
        headers={
            "Authorization":
                f"Bearer {access_token}"
        },
        timeout=10
    )

    if response.status_code != 200:

        return None

    return response.json()


# =========================================================
# GET GUILDS
# =========================================================

def get_discord_guilds(
    access_token
):

    if not access_token:

        return []

    response = requests.get(
        f"{DISCORD_API_URL}/users/@me/guilds",
        headers={
            "Authorization":
                f"Bearer {access_token}"
        },
        timeout=10
    )

    if response.status_code != 200:

        return []

    return response.json()
