import os
import random
import secrets
import sqlite3
import time
import json
  
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode, urlparse

import requests
import psycopg2
import psycopg2.extras

from flask import (
    Flask,
    redirect,
    session,
    request,
    jsonify,
    render_template,
    send_from_directory,
    g
)

from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix


APP_START_TIME = time.time()


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv(
    override=True
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

STATIC_DIR = os.path.join(
    BASE_DIR,
    "static"
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

# Mantido apenas para compatibilidade.
# O LOGIN usa exclusivamente:
# DISCORD_LOGIN_REDIRECT_URI
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

try:
    PORT = int(
        os.getenv(
            "PORT",
            "5000"
        )
    )
except (
    ValueError,
    TypeError
):
    PORT = 5000


# =========================================================
# PAYPAL CONFIGURATION
# =========================================================

PAYPAL_CLIENT_ID = os.getenv(
    "PAYPAL_CLIENT_ID"
)

PAYPAL_CLIENT_SECRET = os.getenv(
    "PAYPAL_CLIENT_SECRET"
)

PAYPAL_MODE = os.getenv(
    "PAYPAL_MODE",
    "sandbox"
).strip().lower()

if PAYPAL_MODE not in (
    "sandbox",
    "live"
):

    PAYPAL_MODE = "sandbox"

if PAYPAL_MODE == "live":

    PAYPAL_API_BASE = (
        "https://api-m.paypal.com"
    )

else:

    PAYPAL_API_BASE = (
        "https://api-m.sandbox.paypal.com"
    )

PAYPAL_CURRENCY = os.getenv(
    "PAYPAL_CURRENCY",
    "EUR"
).strip().upper()

if not PAYPAL_CURRENCY:

    PAYPAL_CURRENCY = "EUR"


# =========================================================
# ADVERTISEMENT PRICES
# =========================================================

ADVERTISEMENT_PRICES = {
    7: Decimal("0.99"),
    14: Decimal("1.50"),
    30: Decimal("2.50")
}


# =========================================================
# COOKIE CONFIGURATION
# =========================================================

_env_cookie_secure = os.getenv(
    "COOKIE_SECURE",
    ""
).strip().lower()

if _env_cookie_secure in (
    "true",
    "false"
):

    COOKIE_SECURE = (
        _env_cookie_secure == "true"
    )

else:

    COOKIE_SECURE = (
        str(
            DISCORD_LOGIN_REDIRECT_URI
            or ""
        )
        .lower()
        .startswith("https://")
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
        "⚠️ DATABASE_URL is missing."
    )

    print(
        "⚠️ PostgreSQL is required for Misuki."
    )


# =========================================================
# FLASK
# =========================================================

app = Flask(
    __name__,
    template_folder=WEBSITE_DIR,
    static_folder=None,
    static_url_path="/static"
)

app.secret_key = SECRET_KEY

app.config["PROPAGATE_EXCEPTIONS"] = True

app.config["SESSION_COOKIE_HTTPONLY"] = True

app.config["SESSION_COOKIE_SAMESITE"] = (
    "None"
    if COOKIE_SECURE
    else "Lax"
)

app.config["SESSION_COOKIE_SECURE"] = (
    COOKIE_SECURE
)

app.config["SESSION_REFRESH_EACH_REQUEST"] = True

app.config["SESSION_COOKIE_NAME"] = (
    "misuki_session"
)

app.config["PERMANENT_SESSION_LIFETIME"] = (
    timedelta(days=1)
)

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1
)


# =========================================================
# REQUEST CACHE
# =========================================================
#
# Estes caches existem apenas durante o request atual.
#
# Antes:
#
#   get_user()
#       -> Discord API
#
#   is_admin()
#       -> get_user()
#       -> Discord API outra vez
#
# Agora:
#
#   get_user()
#       -> Discord API
#
#   is_admin()
#       -> usa o mesmo resultado
#
# O mesmo acontece com guilds do utilizador, guilds do bot
# e licenças.
# =========================================================


# =========================================================
# TEMPLATE HELPERS
# =========================================================

@app.context_processor
def inject_template_helpers():

    return {
        "is_admin": is_admin
    }


# =========================================================
# STATIC FILES
# =========================================================

@app.route("/static/<path:filename>")
def static_files(filename):

    # Keep compatibility with both asset folder layouts.
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
        STATIC_DIR,
        filename
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
        sslmode="require",
        connect_timeout=10
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
                # VERIFICATION REQUESTS
                # -------------------------------------------------

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS verification_requests (

                        id BIGSERIAL PRIMARY KEY,

                        guild_id BIGINT NOT NULL,

                        user_id BIGINT NOT NULL,

                        username TEXT,

                        status TEXT NOT NULL DEFAULT 'pending',

                        created_at DOUBLE PRECISION NOT NULL,

                        processed_at DOUBLE PRECISION,

                        UNIQUE (guild_id, user_id)

                    )
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

                # -------------------------------------------------
                # PAYPAL MIGRATION
                # -------------------------------------------------

                cursor.execute(
                    """
                    ALTER TABLE advertisement_payments
                    ADD COLUMN IF NOT EXISTS provider_order_id TEXT
                    """
                )

                cursor.execute(
                    """
                    ALTER TABLE advertisement_payments
                    ADD COLUMN IF NOT EXISTS provider_capture_id TEXT
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

    return parsed.astimezone(
        timezone.utc
    )


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
        in (
            "http",
            "https"
        )
        and bool(
            parsed.netloc
        )
    )


def safe_next_url(value):

    if not value:
        return "/dashboard"

    value = str(
        value
    ).strip()

    if not value.startswith("/"):
        return "/dashboard"

    if value.startswith("//"):
        return "/dashboard"

    return value


# =========================================================
# PAYPAL HELPERS
# =========================================================

def paypal_is_configured():

    return bool(
        PAYPAL_CLIENT_ID
        and PAYPAL_CLIENT_SECRET
    )


def paypal_get_access_token():

    if not paypal_is_configured():

        raise RuntimeError(
            "PayPal is not configured."
        )

    try:

        response = requests.post(
            f"{PAYPAL_API_BASE}/v1/oauth2/token",
            auth=(
                PAYPAL_CLIENT_ID,
                PAYPAL_CLIENT_SECRET
            ),
            data={
                "grant_type":
                    "client_credentials"
            },
            headers={
                "Accept":
                    "application/json",
                "Accept-Language":
                    "en_US",
                "Content-Type":
                    "application/x-www-form-urlencoded"
            },
            timeout=15
        )

    except requests.RequestException as error:

        print(
            f"❌ PayPal authentication request error: {error}"
        )

        raise RuntimeError(
            "Could not contact PayPal."
        ) from error

    if response.status_code != 200:

        print(
            "❌ PayPal authentication failed:"
        )

        print(
            response.text
        )

        raise RuntimeError(
            "PayPal authentication failed."
        )

    try:

        data = response.json()

    except ValueError as error:

        raise RuntimeError(
            "PayPal returned invalid authentication data."
        ) from error

    access_token = data.get(
        "access_token"
    )

    if not access_token:

        raise RuntimeError(
            "PayPal did not return an access token."
        )

    return access_token


def paypal_create_order(
    advertisement_id,
    title,
    duration_days,
    amount
):

    if not paypal_is_configured():

        raise RuntimeError(
            "PayPal is not configured."
        )

    access_token = paypal_get_access_token()

    amount = Decimal(
        amount
    ).quantize(
        Decimal("0.01")
    )

    return_url = (
        f"{request.host_url.rstrip('/')}"
        "/advertise/paypal/success"
    )

    cancel_url = (
        f"{request.host_url.rstrip('/')}"
        "/advertise/paypal/cancel"
    )

    payload = {
        "intent": "CAPTURE",

        "purchase_units": [
            {
                "reference_id":
                    f"misuki-ad-{advertisement_id}",

                "description":
                    f"Misuki advertisement - {duration_days} days",

                "custom_id":
                    str(advertisement_id),

                "amount": {
                    "currency_code":
                        PAYPAL_CURRENCY,

                    "value":
                        f"{amount:.2f}"
                }
            }
        ],

        "application_context": {
            "brand_name":
                "Misuki",

            "user_action":
                "PAY_NOW",

            "shipping_preference":
                "NO_SHIPPING",

            "return_url":
                return_url,

            "cancel_url":
                cancel_url
        }
    }

    headers = {
        "Authorization":
            f"Bearer {access_token}",

        "Content-Type":
            "application/json",

        "Accept":
            "application/json",

        "PayPal-Request-Id":
            secrets.token_urlsafe(24)
    }

    try:

        response = requests.post(
            f"{PAYPAL_API_BASE}/v2/checkout/orders",
            json=payload,
            headers=headers,
            timeout=20
        )

    except requests.RequestException as error:

        print(
            f"❌ PayPal create order request error: {error}"
        )

        raise RuntimeError(
            "Could not create the PayPal payment."
        ) from error

    if response.status_code not in (
        200,
        201
    ):

        print(
            "❌ PayPal create order failed:"
        )

        print(
            response.text
        )

        raise RuntimeError(
            "PayPal could not create the payment."
        )

    try:

        data = response.json()

    except ValueError as error:

        raise RuntimeError(
            "PayPal returned invalid order data."
        ) from error

    order_id = data.get(
        "id"
    )

    if not order_id:

        raise RuntimeError(
            "PayPal did not return an order ID."
        )

    approval_url = None

    for link in data.get(
        "links",
        []
    ):

        if link.get(
            "rel"
        ) in (
            "approve",
            "payer-action"
        ):

            approval_url = link.get(
                "href"
            )

            if approval_url:
                break

    if not approval_url:

        raise RuntimeError(
            "PayPal did not return an approval URL."
        )

    return {
        "id":
            order_id,

        "approval_url":
            approval_url,

        "status":
            data.get(
                "status"
            )
    }


def paypal_capture_order(
    order_id
):

    if not paypal_is_configured():

        raise RuntimeError(
            "PayPal is not configured."
        )

    if not order_id:

        raise RuntimeError(
            "PayPal order ID is missing."
        )

    access_token = paypal_get_access_token()

    headers = {
        "Authorization":
            f"Bearer {access_token}",

        "Content-Type":
            "application/json",

        "Accept":
            "application/json",

        "PayPal-Request-Id":
            secrets.token_urlsafe(24)
    }

    try:

        response = requests.post(
            f"{PAYPAL_API_BASE}/v2/checkout/orders/"
            f"{order_id}/capture",
            json={},
            headers=headers,
            timeout=20
        )

    except requests.RequestException as error:

        print(
            f"❌ PayPal capture request error: {error}"
        )

        raise RuntimeError(
            "Could not capture the PayPal payment."
        ) from error

    if response.status_code not in (
        200,
        201
    ):

        print(
            "❌ PayPal capture failed:"
        )

        print(
            response.text
        )

        raise RuntimeError(
            "PayPal could not complete the payment."
        )

    try:

        data = response.json()

    except ValueError as error:

        raise RuntimeError(
            "PayPal returned invalid capture data."
        ) from error

    return data


def paypal_extract_capture_id(
    paypal_response
):

    purchase_units = (
        paypal_response.get(
            "purchase_units",
            []
        )
    )

    for purchase_unit in purchase_units:

        payments = (
            purchase_unit.get(
                "payments",
                {}
            )
        )

        captures = (
            payments.get(
                "captures",
                []
            )
        )

        for capture in captures:

            capture_id = capture.get(
                "id"
            )

            if capture_id:
                return capture_id

    return None


def paypal_extract_captured_amount(
    paypal_response
):

    purchase_units = (
        paypal_response.get(
            "purchase_units",
            []
        )
    )

    for purchase_unit in purchase_units:

        payments = (
            purchase_unit.get(
                "payments",
                {}
            )
        )

        captures = (
            payments.get(
                "captures",
                []
            )
        )

        for capture in captures:

            amount = capture.get(
                "amount"
            )

            if not amount:
                continue

            value = amount.get(
                "value"
            )

            currency = amount.get(
                "currency_code"
            )

            if value is None:
                continue

            try:

                value = Decimal(
                    str(value)
                ).quantize(
                    Decimal("0.01")
                )

            except (
                InvalidOperation,
                ValueError,
                TypeError
            ):

                continue

            return value, currency

    return None, None


def paypal_payment_status_for_ad(
    advertisement_id,
    user_id
):

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
                        id,
                        advertisement_id,
                        user_id,
                        provider,
                        provider_payment_id,
                        provider_order_id,
                        provider_capture_id,
                        amount,
                        currency,
                        status,
                        created_at,
                        updated_at
                    FROM advertisement_payments
                    WHERE advertisement_id = %s
                    AND user_id = %s
                    AND provider = 'paypal'
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (
                        advertisement_id,
                        user_id
                    )
                )

                return cursor.fetchone()

    except Exception as error:

        print(
            f"❌ PayPal payment lookup error: {error}"
        )

        return None


def update_payment_record(
    payment_id,
    status,
    provider_order_id=None,
    provider_capture_id=None,
    provider_payment_id=None,
    amount=None,
    currency=None
):

    if not DATABASE_URL:
        return False

    now = utc_now().isoformat()

    try:

        with database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE advertisement_payments
                    SET
                        provider_payment_id =
                            COALESCE(%s, provider_payment_id),

                        provider_order_id =
                            COALESCE(%s, provider_order_id),

                        provider_capture_id =
                            COALESCE(%s, provider_capture_id),

                        amount =
                            COALESCE(%s, amount),

                        currency =
                            COALESCE(%s, currency),

                        status = %s,

                        updated_at = %s

                    WHERE id = %s
                    """,
                    (
                        provider_payment_id,
                        provider_order_id,
                        provider_capture_id,
                        amount,
                        currency,
                        status,
                        now,
                        payment_id
                    )
                )

            connection.commit()

        return True

    except Exception as error:

        print(
            f"❌ Payment update error: {error}"
        )

        return False


# =========================================================
# LICENSE HELPERS — OPTIMIZED
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

    # -----------------------------------------------------
    # REQUEST CACHE
    # -----------------------------------------------------

    license_cache = getattr(
        g,
        "license_cache",
        None
    )

    if license_cache is not None:

        return license_cache.get(
            guild_id
        )

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


def get_licenses_for_guilds(
    guild_ids
):
    """
    Carrega as licenças de vários servidores numa única
    query PostgreSQL.

    Antes do optimization:

        get_license(guild_1)
        get_license(guild_2)
        get_license(guild_3)
        ...

    Cada get_license() abria uma nova ligação PostgreSQL.

    Agora:

        SELECT ... WHERE guild_id = ANY(...)

    Uma única consulta trata de todos os servidores.
    """

    # -----------------------------------------------------
    # CACHE POR REQUEST
    # -----------------------------------------------------

    existing_cache = getattr(
        g,
        "license_cache",
        None
    )

    if existing_cache is not None:

        return existing_cache

    result = {}

    if not DATABASE_URL:

        g.license_cache = result

        return result

    normalized_ids = []

    for guild_id in guild_ids:

        try:

            normalized_ids.append(
                int(guild_id)
            )

        except (
            TypeError,
            ValueError
        ):

            continue

    # Remove duplicados
    normalized_ids = list(
        dict.fromkeys(
            normalized_ids
        )
    )

    if not normalized_ids:

        g.license_cache = result

        return result

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
                    WHERE guild_id = ANY(%s)
                    """,
                    (
                        normalized_ids,
                    )
                )

                rows = cursor.fetchall()

    except Exception as error:

        print(
            f"❌ Could not load guild licenses: {error}"
        )

        g.license_cache = result

        return result

    now = utc_now()

    expired_ids = []

    for row in rows:

        guild_id = int(
            row["guild_id"]
        )

        status = str(
            row["status"]
            or ""
        ).lower()

        expires_at = row[
            "expires_at"
        ]

        # -------------------------------------------------
        # CHECK EXPIRATION
        # -------------------------------------------------

        if (
            status == "active"
            and
            expires_at
        ):

            expiration = parse_datetime(
                expires_at
            )

            if (
                expiration
                and
                now >= expiration
            ):

                status = "expired"

                expired_ids.append(
                    guild_id
                )

        result[guild_id] = (
            guild_id,
            row["license_key"],
            status,
            expires_at,
            row["created_at"]
        )

    # -----------------------------------------------------
    # MARK EXPIRED
    # -----------------------------------------------------

    if expired_ids:

        try:

            with database_connection() as connection:

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        UPDATE licenses
                        SET status = 'expired'
                        WHERE guild_id = ANY(%s)
                        AND status = 'active'
                        """,
                        (
                            expired_ids,
                        )
                    )

                connection.commit()

        except Exception as error:

            print(
                f"⚠️ Could not mark licenses as expired: {error}"
            )

    g.license_cache = result

    return result


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

    if str(
        status
    ).lower() != "active":

        return False

    if expires_at:

        expiration = parse_datetime(
            expires_at
        )

        if not expiration:
            return False

        if utc_now() >= expiration:

            # -------------------------------------------------
            # If the license wasn't already bulk-loaded,
            # update it here.
            # -------------------------------------------------

            try:

                with database_connection() as connection:

                    with connection.cursor() as cursor:

                        cursor.execute(
                            """
                            UPDATE licenses
                            SET status = 'expired'
                            WHERE guild_id = %s
                            AND status = 'active'
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

            # Keep request cache consistent.
            cache = getattr(
                g,
                "license_cache",
                None
            )

            if cache is not None:

                existing = cache.get(
                    int(guild_id)
                )

                if existing:

                    cache[
                        int(guild_id)
                    ] = (
                        existing[0],
                        existing[1],
                        "expired",
                        existing[3],
                        existing[4]
                    )

            return False

    return True


def get_active_license_guild_ids():

    cached = getattr(
        g,
        "active_license_ids",
        None
    )

    if cached is not None:

        return cached

    active_ids = set()

    if not DATABASE_URL:

        g.active_license_ids = (
            active_ids
        )

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

        g.active_license_ids = (
            active_ids
        )

        return active_ids

    now = utc_now()

    expired_ids = []

    for row in rows:

        guild_id = row[0]

        status = row[1]

        expires_at = row[2]

        if str(
            status
        ).lower() != "active":

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

    # -----------------------------------------------------
    # MARK EXPIRED LICENSES
    # -----------------------------------------------------

    if expired_ids:

        try:

            with database_connection() as connection:

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        UPDATE licenses
                        SET status = 'expired'
                        WHERE guild_id = ANY(%s)
                        AND status = 'active'
                        """,
                        (
                            expired_ids,
                        )
                    )

                connection.commit()

        except Exception as error:

            print(
                f"⚠️ Could not mark licenses as expired: {error}"
            )

    g.active_license_ids = (
        active_ids
    )

    return active_ids


# =========================================================
# DISCORD USER — OPTIMIZED
# =========================================================

def get_user():

    # -----------------------------------------------------
    # CACHE
    # -----------------------------------------------------

    if getattr(
        g,
        "user_loaded",
        False
    ):

        return getattr(
            g,
            "user",
            None
        )

    g.user_loaded = True

    access_token = session.get(
        "access_token"
    )

    if not access_token:

        g.user = None

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

        g.user = None

        return None

    if response.status_code != 200:

        if response.status_code in (
            401,
            403
        ):

            session.clear()

        g.user = None

        return None

    try:

        g.user = response.json()

    except ValueError:

        g.user = None

    return g.user


# =========================================================
# USER GUILDS — OPTIMIZED
# =========================================================

def get_user_guilds():

    # -----------------------------------------------------
    # CACHE
    # -----------------------------------------------------

    if getattr(
        g,
        "user_guilds_loaded",
        False
    ):

        return getattr(
            g,
            "user_guilds",
            []
        )

    g.user_guilds_loaded = True

    access_token = session.get(
        "access_token"
    )

    if not access_token:

        g.user_guilds = []

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

        g.user_guilds = []

        return []

    if response.status_code in (
        401,
        403
    ):

        session.clear()

        g.user_guilds = []

        return []

    if response.status_code != 200:

        g.user_guilds = []

        return []

    try:

        data = response.json()

    except ValueError:

        g.user_guilds = []

        return []

    g.user_guilds = (
        data
        if isinstance(data, list)
        else []
    )

    return g.user_guilds


# =========================================================
# BOT GUILDS — OPTIMIZED
# =========================================================

def get_bot_guilds():

    # -----------------------------------------------------
    # CACHE
    # -----------------------------------------------------

    if getattr(
        g,
        "bot_guilds_loaded",
        False
    ):

        return getattr(
            g,
            "bot_guilds",
            []
        )

    g.bot_guilds_loaded = True

    if not BOT_TOKEN:

        g.bot_guilds = []

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
            f"❌ Discord bot guild request error: {error}"
        )

        g.bot_guilds = []

        return []

    if response.status_code != 200:

        g.bot_guilds = []

        return []

    try:

        data = response.json()

    except ValueError:

        g.bot_guilds = []

        return []

    g.bot_guilds = (
        data
        if isinstance(data, list)
        else []
    )

    return g.bot_guilds


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
# PERMISSIONS
# =========================================================

ADMINISTRATOR = 1 << 3
MANAGE_GUILD = 1 << 5


def is_admin(user=None):

    if user is None:

        user = get_user()

    if not user:
        return False

    user_id = user.get(
        "id"
    )

    if not user_id:
        return False

    return str(
        user_id
    ) in ADMIN_DISCORD_IDS


def can_manage_guild(guild):

    if not guild:
        return False

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

    if not CLIENT_ID:
        return None

    try:

        guild_id = int(
            guild_id
        )

    except (
        TypeError,
        ValueError
    ):

        return None

    permissions = os.getenv(
        "DISCORD_BOT_PERMISSIONS",
        "0"
    ).strip()

    try:

        int(
            permissions
        )

    except (
        ValueError,
        TypeError
    ):

        permissions = "0"

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

    session["oauth_state_expires_at"] = (
        (
            utc_now()
            +
            timedelta(minutes=10)
        )
        .isoformat()
    )

    session.permanent = True

    session.modified = True

    return state


def verify_oauth_state(state):

    if not state:

        print(
            "⚠️ OAuth state verification: No state provided"
        )

        return False

    stored_state = session.get(
        "oauth_state"
    )

    expires_at_raw = session.get(
        "oauth_state_expires_at"
    )

    if not stored_state:

        print(
            "⚠️ OAuth state not in session"
        )

        return False

    if not expires_at_raw:

        print(
            "⚠️ OAuth state expiration missing"
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

    try:

        expires_at = datetime.fromisoformat(
            str(expires_at_raw)
        )

        if expires_at.tzinfo is None:

            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        expires_at = expires_at.astimezone(
            timezone.utc
        )

    except (
        ValueError,
        TypeError
    ) as error:

        print(
            f"⚠️ OAuth state date parse error: {error}"
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

    if utc_now() >= expires_at:

        print(
            "⚠️ OAuth state expired"
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

    try:

        valid = secrets.compare_digest(
            str(stored_state),
            str(state)
        )

    except Exception:

        valid = False

    if not valid:

        print(
            "⚠️ OAuth state mismatch"
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
        "✅ OAuth state verified successfully"
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
        message=message,
        is_admin=is_admin
    ), status_code


# =========================================================
# DISCORD VERIFICATION
# =========================================================

def verification_guild(guild_id, access_token):

    try:

        guild_id = str(int(guild_id))

    except (TypeError, ValueError):

        return None

    for guild in get_user_guilds():

        if str(guild.get("id", "")) == guild_id:

            return guild

    return None


def verification_bot_is_in_guild(guild_id):

    guild_id = str(guild_id)

    return any(
        str(guild.get("id", "")) == guild_id
        for guild in get_bot_guilds()
    )


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
        + urlencode({"guild_id": guild_id})
    )


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

    guild_id = request.args.get(
        "guild_id",
        ""
    ).strip()

    if not user:

        session["next_url"] = (
            f"/verify?guild_id={guild_id}"
            if guild_id
            else "/verify"
        )

        return redirect("/login")

    if not guild_id:

        return error_page(
            "❌ Verification Error",
            "No server was specified for verification.",
            400,
            user
        )

    try:

        guild_id_int = int(guild_id)

    except (TypeError, ValueError):

        return error_page(
            "❌ Verification Error",
            "The server ID is invalid.",
            400,
            user
        )

    guild = verification_guild(
        guild_id_int,
        session.get("access_token")
    )

    if guild is None:

        return error_page(
            "❌ Access denied",
            "You are not a member of this Discord server.",
            403,
            user
        )

    if not verification_bot_is_in_guild(guild_id_int):

        return error_page(
            "❌ Verification unavailable",
            "The Misuki bot is not installed on this server.",
            400,
            user
        )

    return render_template(
        "verification.html",
        user=user,
        username=(
            user.get("global_name")
            or user.get("username")
            or "Discord User"
        ),
        guild_name=guild.get("name") or "Discord Server",
        guild_id=str(guild_id_int),
        is_admin=is_admin
    )


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

    guild_id = request.form.get(
        "guild_id",
        ""
    ).strip()

    if not user:

        session["next_url"] = (
            f"/verify?guild_id={guild_id}"
            if guild_id
            else "/verify"
        )

        return redirect("/login")

    try:

        guild_id_int = int(guild_id)

    except (TypeError, ValueError):

        return error_page(
            "❌ Verification Error",
            "The server ID is invalid.",
            400,
            user
        )

    guild = verification_guild(
        guild_id_int,
        session.get("access_token")
    )

    if guild is None or not verification_bot_is_in_guild(guild_id_int):

        return error_page(
            "❌ Verification unavailable",
            "The server could not be verified.",
            400,
            user
        )

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
                        processed_at
                    )
                    VALUES (%s, %s, %s, 'pending', %s, NULL)
                    ON CONFLICT (guild_id, user_id)
                    DO UPDATE SET
                        username = EXCLUDED.username,
                        status = 'pending',
                        created_at = EXCLUDED.created_at,
                        processed_at = NULL
                    """,
                    (
                        guild_id_int,
                        int(user.get("id")),
                        user.get("global_name")
                        or user.get("username")
                        or "Discord User",
                        time.time()
                    )
                )

            connection.commit()

    except (TypeError, ValueError):

        return error_page(
            "❌ Verification Error",
            "Your Discord account could not be identified.",
            400,
            user
        )

    except Exception as error:

        print(
            f"❌ Verification request error: {error}"
        )

        return error_page(
            "❌ Verification Error",
            "The verification request could not be created. Please try again.",
            500,
            user
        )

    return render_template(
        "verification.html",
        user=user,
        username=(
            user.get("global_name")
            or user.get("username")
            or "Discord User"
        ),
        guild_name=guild.get("name") or "Discord Server",
        guild_id=str(guild_id_int),
        verification_submitted=True,
        is_admin=is_admin
    )


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

    if not valid_http_url(
        DISCORD_LOGIN_REDIRECT_URI
    ):

        return error_page(
            "❌ Configuration Error",
            "DISCORD_LOGIN_REDIRECT_URI must be a valid HTTP or HTTPS URL.",
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
        +
        urlencode(params)
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

    except requests.RequestException as error:

        print(
            f"❌ Discord user request error: {error}"
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
            "Discord returned invalid user data.",
            400
        )

    next_url = safe_next_url(
        session.get(
            "next_url"
        )
    )

    # -----------------------------------------------------
    # CLEAR OLD AUTH SESSION
    # -----------------------------------------------------

    session.clear()

    # -----------------------------------------------------
    # CREATE NEW AUTH SESSION
    # -----------------------------------------------------

    session["access_token"] = (
        access_token
    )

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

def get_random_reviews(
    amount=6
):

    if not DATABASE_URL:
        return []

    try:

        amount = int(
            amount
        )

    except (
        ValueError,
        TypeError
    ):

        amount = 6

    amount = max(
        1,
        min(
            50,
            amount
        )
    )

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
                    ORDER BY RANDOM()
                    LIMIT %s
                    """,
                    (
                        amount,
                    )
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

    return reviews


# =========================================================
# ADVERTISEMENTS
# =========================================================

def get_active_advertisements():

    if not DATABASE_URL:
        return []

    # Expira primeiro e depois faz a query dos anúncios.
    # O index() já não chama expire_advertisements()
    # separadamente, evitando duas operações seguidas.
    expire_advertisements()

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
                    ORDER BY id DESC
                    """
                )

                rows = cursor.fetchall()

    except Exception as error:

        print(
            f"❌ Advertisement database error: {error}"
        )

        return []

    now = utc_now()

    active_advertisements = []

    for advertisement in rows:

        start_at = parse_datetime(
            advertisement.get(
                "start_at"
            )
        )

        end_at = parse_datetime(
            advertisement.get(
                "end_at"
            )
        )

        if start_at is not None:

            if now < start_at:
                continue

        if end_at is not None:

            if now >= end_at:
                continue

        active_advertisements.append(
            advertisement
        )

    return active_advertisements


def expire_advertisements():

    if not DATABASE_URL:
        return

    now = utc_now()

    try:

        with database_connection() as connection:

            with connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            ) as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        end_at
                    FROM advertisements
                    WHERE status = 'active'
                    AND end_at IS NOT NULL
                    """
                )

                advertisements = (
                    cursor.fetchall()
                )

                expired_ids = []

                for advertisement in advertisements:

                    end_at = parse_datetime(
                        advertisement.get(
                            "end_at"
                        )
                    )

                    if not end_at:
                        continue

                    if now >= end_at:

                        expired_ids.append(
                            advertisement["id"]
                        )

                if expired_ids:

                    cursor.execute(
                        """
                        UPDATE advertisements
                        SET
                            status = 'expired',
                            updated_at = %s
                        WHERE id = ANY(%s)
                        """,
                        (
                            now.isoformat(),
                            expired_ids
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
# USER HAS ACTIVE LICENSE — OPTIMIZED
# =========================================================

def user_has_license():

    guilds = get_user_guilds()

    guild_ids = [
        guild.get("id")
        for guild in guilds
        if guild.get("id")
    ]

    if not guild_ids:
        return False

    # Uma única query para todas as guilds.
    licenses = get_licenses_for_guilds(
        guild_ids
    )

    now = utc_now()

    for guild_id in guild_ids:

        try:

            license_data = licenses.get(
                int(guild_id)
            )

        except (
            TypeError,
            ValueError
        ):

            continue

        if not license_data:
            continue

        status = str(
            license_data[2]
            or ""
        ).lower()

        if status != "active":
            continue

        expires_at = license_data[3]

        if expires_at:

            expiration = parse_datetime(
                expires_at
            )

            if (
                not expiration
                or
                now >= expiration
            ):

                continue

        return True

    return False


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    user = get_user()

    # get_active_advertisements() já faz a expiração.
    # Antes isto era chamado duas vezes.
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
        advertisements=advertisements,
        is_admin=is_admin
    )


# =========================================================
# DASHBOARD — OPTIMIZED
# =========================================================

@app.route("/dashboard")
def dashboard():

    dashboard_start = time.perf_counter()

    user = get_user()

    if not user:

        session["next_url"] = (
            "/dashboard"
        )

        return redirect(
            "/login"
        )

    # -----------------------------------------------------
    # DISCORD REQUESTS
    # -----------------------------------------------------

    user_guilds = get_user_guilds()

    bot_guilds = get_bot_guilds()

    bot_guild_ids = {
        str(
            guild.get("id")
        )
        for guild in bot_guilds
        if guild.get("id")
    }

    # -----------------------------------------------------
    # LOAD ALL USER LICENSES AT ONCE
    # -----------------------------------------------------

    guild_ids = [
        guild.get("id")
        for guild in user_guilds
        if guild.get("id")
    ]

    licenses = get_licenses_for_guilds(
        guild_ids
    )

    # -----------------------------------------------------
    # ACTIVE LICENSE IDS
    # -----------------------------------------------------
    #
    # Não fazemos uma segunda query a toda a tabela licenses.
    # Usamos os dados que acabámos de carregar.
    # -----------------------------------------------------

    active_license_ids = set()

    now = utc_now()

    for guild_id, license_data in licenses.items():

        status = str(
            license_data[2]
            or ""
        ).lower()

        if status != "active":
            continue

        expires_at = license_data[3]

        if expires_at:

            expiration = parse_datetime(
                expires_at
            )

            if (
                not expiration
                or
                now >= expiration
            ):

                continue

        active_license_ids.add(
            str(guild_id)
        )

    authorized = []

    available = []

    # -----------------------------------------------------
    # PROCESS GUILDS
    # -----------------------------------------------------

    for original_guild in user_guilds:

        guild = dict(
            original_guild
        )

        guild_id = str(
            guild.get("id")
            or ""
        ).strip()

        if not guild_id:
            continue

        try:

            license_data = licenses.get(
                int(guild_id)
            )

        except (
            TypeError,
            ValueError
        ):

            license_data = None

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

        # -------------------------------------------------
        # BOT ALREADY INSTALLED
        # -------------------------------------------------

        if guild_id in bot_guild_ids:

            authorized.append(
                guild
            )

            continue

        # -------------------------------------------------
        # BOT NOT INSTALLED
        # -------------------------------------------------

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

    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    authorized.sort(
        key=lambda guild:
            str(
                guild.get(
                    "name",
                    ""
                )
            ).lower()
    )

    available.sort(
        key=lambda guild: (
            not guild.get(
                "can_add",
                False
            ),
            str(
                guild.get(
                    "name",
                    ""
                )
            ).lower()
        )
    )

    # -----------------------------------------------------
    # PERFORMANCE LOG
    # -----------------------------------------------------
    #
    # Isto aparece nos logs do Render e permite perceber
    # quanto tempo o dashboard realmente demora.
    # -----------------------------------------------------

    elapsed = (
        time.perf_counter()
        -
        dashboard_start
    )

    print(
        f"⚡ Dashboard loaded in "
        f"{elapsed:.3f}s | "
        f"user_guilds={len(user_guilds)} | "
        f"bot_guilds={len(bot_guilds)} | "
        f"licenses={len(licenses)}"
    )

    return render_template(
        "dashboard.html",
        user=user,
        authorized=authorized,
        available=available,
        is_admin=is_admin
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

        return redirect(
            "/login"
        )

    try:

        guild_id_int = int(
            guild_id
        )

    except (
        ValueError,
        TypeError
    ):

        return error_page(
            "❌ Invalid server",
            "The server ID is invalid.",
            400,
            user
        )

    user_guilds = get_user_guilds()

    guild = next(
        (
            guild
            for guild in user_guilds
            if str(
                guild.get("id")
            ) == str(guild_id_int)
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

    if str(
        guild_id_int
    ) not in bot_guild_ids:

        return redirect(
            "/dashboard"
        )

    # -----------------------------------------------------
    # Load once into request cache.
    # license_is_active() will reuse it.
    # -----------------------------------------------------

    get_licenses_for_guilds([
        guild_id_int
    ])

    license_data = get_license(
        guild_id_int
    )

    license_active = license_is_active(
        guild_id_int
    )

    return render_template(
        "manage.html",
        user=user,
        guild=guild,
        license_data=license_data,
        license_active=license_active,
        is_admin=is_admin
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
        can_review=can_review,
        is_admin=is_admin
    )


# =========================================================
# STATISTICS PAGE
# =========================================================

@app.route("/statistics")
def statistics():

    current_user = get_user()

    user_is_admin = is_admin(
        current_user
    )

    statistics_data = {

        "servers": 0,
        "users": 0,
        "channels": 0,
        "latency": 0,
        "commands": 0,
        "tickets": 0,
        "verifications": 0,

        "bot_status": "Offline",

        "database_status": "Operational",

        "api_status": "Offline",

        "version": os.getenv(
            "MISUKI_VERSION",
            "1.0.0"
        ),

        "uptime": "0s",

        "updated_at": None,
    }


    # =====================================================
    # BOT SNAPSHOT
    # =====================================================

    bot_snapshot = {}

    try:

        bot_stats_file = os.path.join(
            BASE_DIR,
            "data",
            "bot_stats.json"
        )

        with open(
            bot_stats_file,
            encoding="utf-8"
        ) as file:

            bot_snapshot = json.load(
                file
            )


        for key in (
            "servers",
            "users",
            "channels",
            "latency",
            "commands",
            "bot_status",
            "uptime",
            "verifications",
            "updated_at",
        ):

            if key in bot_snapshot:

                statistics_data[key] = (
                    bot_snapshot[key]
                )

        statistics_data["version"] = os.getenv(
            "MISUKI_VERSION",
            "1.0.0"
        )


    except (
        OSError,
        json.JSONDecodeError,
        TypeError,
        ValueError
    ):

        pass


    # =====================================================
    # HEARTBEAT
    # =====================================================

    current_time = time.time()

    last_seen = bot_snapshot.get(
        "last_seen"
    )


    if last_seen is not None:

        try:

            heartbeat_age = (
                current_time
                - float(last_seen)
            )


            # -------------------------------------------------
            # 60 SEGUNDOS SEM HEARTBEAT = OFFLINE
            # -------------------------------------------------

            if heartbeat_age <= 60:

                statistics_data[
                    "bot_status"
                ] = "Online"

            else:

                statistics_data[
                    "bot_status"
                ] = "Offline"


        except (
            TypeError,
            ValueError
        ):

            statistics_data[
                "bot_status"
            ] = "Offline"

    else:

        statistics_data[
            "bot_status"
        ] = "Offline"


    # =====================================================
    # API STATUS
    # =====================================================

    if statistics_data[
        "bot_status"
    ] == "Online":

        statistics_data[
            "api_status"
        ] = "Operational"

    else:

        statistics_data[
            "api_status"
        ] = "Unavailable"


    # =====================================================
    # DATABASE STATUS
    # =====================================================

    database_ok = True


    # -----------------------------------------------------
    # TICKETS DATABASE
    # -----------------------------------------------------

    try:

        tickets_database = os.path.join(
            BASE_DIR,
            "data",
            "tickets.db"
        )


        with sqlite3.connect(
            tickets_database
        ) as connection:

            result = connection.execute(
                """
                SELECT
                    COALESCE(
                        SUM(number),
                        0
                    )
                FROM ticket_counter
                """
            ).fetchone()


            statistics_data[
                "tickets"
            ] = int(
                result[0] or 0
            )


    except (
        OSError,
        sqlite3.Error,
        TypeError,
        ValueError
    ):

        database_ok = False

        statistics_data[
            "tickets"
        ] = 0


    # -----------------------------------------------------
    # MODERATION DATABASE
    # -----------------------------------------------------

    moderation_actions = 0


    try:

        moderation_database = os.path.join(
            BASE_DIR,
            "data",
            "moderation.db"
        )


        with sqlite3.connect(
            moderation_database
        ) as connection:

            result = connection.execute(
                """
                SELECT
                    COUNT(*)
                FROM warnings
                """
            ).fetchone()


            moderation_actions = int(
                result[0] or 0
            )


    except (
        OSError,
        sqlite3.Error,
        TypeError,
        ValueError
    ):

        database_ok = False

        moderation_actions = 0


    if database_ok:

        statistics_data[
            "database_status"
        ] = "Operational"

    else:

        statistics_data[
            "database_status"
        ] = "Error"

# =====================================================
# ADMIN USER INFORMATION
# =====================================================

def get_admin_users(admin_servers):
    """
    Obtém os utilizadores dos servidores onde o bot está presente.

    Apenas é chamado para administradores do Misuki.
    Os utilizadores são deduplicados pelo Discord ID.
    Bots são ignorados.
    """

    if not BOT_TOKEN:
        return []

    users_by_id = {}

    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    for server in admin_servers or []:

        guild_id = server.get("id")

        if not guild_id:
            continue

        after = "0"

        while True:

            try:

                response = requests.get(
                    f"{DISCORD_API}/guilds/{guild_id}/members",
                    headers=headers,
                    params={
                        "limit": 1000,
                        "after": after
                    },
                    timeout=10
                )

            except requests.RequestException as error:

                print(
                    f"⚠️ Could not fetch members for guild {guild_id}: {error}"
                )

                break

            if response.status_code != 200:

                print(
                    f"⚠️ Could not fetch members for guild {guild_id}: "
                    f"HTTP {response.status_code}"
                )

                break

            try:

                members = response.json()

            except ValueError:

                print(
                    f"⚠️ Discord returned invalid member data for guild {guild_id}."
                )

                break

            if not members:
                break

            for member in members:

                discord_user = member.get(
                    "user",
                    {}
                )

                if discord_user.get(
                    "bot",
                    False
                ):
                    continue

                user_id = discord_user.get(
                    "id"
                )

                if not user_id:
                    continue

                username = (
                    discord_user.get("global_name")
                    or discord_user.get("username")
                    or "Discord User"
                )

                avatar_hash = discord_user.get(
                    "avatar"
                )

                if avatar_hash:

                    avatar_url = (
                        f"https://cdn.discordapp.com/avatars/"
                        f"{user_id}/{avatar_hash}.png?size=128"
                    )

                else:

                    avatar_url = None

                if user_id not in users_by_id:

                    users_by_id[user_id] = {
                        "id": user_id,
                        "name": username,
                        "avatar": avatar_url
                    }

            if len(members) < 1000:
                break

            after = str(
                members[-1]
                .get("user", {})
                .get("id", "")
            )

            if not after:
                break

    return list(
        users_by_id.values()
    )
    # =====================================================
# ADMIN SERVER INFORMATION
# =====================================================

admin_servers = []


if user_is_admin:

    try:

        admin_servers = (
            bot_snapshot.get(
                "admin_servers",
                []
            )
        )

    except Exception:

        admin_servers = []


# =====================================================
# ADMIN USER INFORMATION
# =====================================================

admin_users=[]


if user_is_admin:

    try:

        admin_users = get_admin_users(
            admin_servers
        )

    except Exception as error:

        print(
            f"⚠️ Could not load administrator user information: {error}"
        )

        admin_users = []

    # =====================================================
    # ADMIN STATISTICS
    # =====================================================

    admin_statistics = {

        "commands": statistics_data[
            "commands"
        ],

        "tickets": statistics_data[
            "tickets"
        ],

        "moderation": moderation_actions,

        "announcements": 0,
    }


    # =====================================================
    # RENDER
    # =====================================================

    return render_template(
        "statistics.html",

        user=current_user,

        # IMPORTANTE:
        # is_admin continua a ser a função.
        # O base.html usa is_admin(user).

        is_admin=is_admin,

        # Resultado True/False para a área
        # administrativa da Statistics.

        is_misuki_admin=user_is_admin,

        statistics=statistics_data,

        admin_statistics=admin_statistics,

        admin_servers=admin_servers,

        admin_users=admin_users
    )

# =========================================================
# LIVE STATISTICS API
# =========================================================

@app.route("/api/statistics")
def statistics_api():

    current_user = get_user()

    user_is_admin = is_admin(
        current_user
    )

    statistics_data = {

        "servers": 0,
        "users": 0,
        "channels": 0,
        "latency": 0,
        "commands": 0,
        "tickets": 0,
        "verifications": 0,

        "bot_status": "Offline",

        "database_status": "Operational",

        "api_status": "Unavailable",

        "version": os.getenv(
            "MISUKI_VERSION",
            "1.0.0"
        ),

        "uptime": "0s",

        "last_seen": None,
    }


    # =====================================================
    # BOT STATISTICS — NEON / POSTGRESQL
    # =====================================================

    bot_snapshot = {}

    try:

        database_url = os.getenv(
            "DATABASE_URL"
        )

        if not database_url:

            raise RuntimeError(
                "DATABASE_URL não está configurado."
            )


        with psycopg2.connect(
            database_url,
            connect_timeout=10
        ) as connection:

            with connection.cursor() as cursor:

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
                    """
                )

                result = cursor.fetchone()


                if result:

                    bot_snapshot = {

                        "servers": result[0],

                        "users": result[1],

                        "channels": result[2],

                        "latency": result[3],

                        "commands": result[4],

                        "verifications": result[5],

                        "bot_status": result[6],

                        "uptime": result[7],

                        "version": result[8],

                        "last_seen": result[9],

                        "admin_servers": result[10] or [],

                        "updated_at": result[11],
                    }


    except (
        OSError,
        psycopg2.Error,
        TypeError,
        ValueError,
        RuntimeError
    ) as error:

        print(
            f"❌ Statistics API database error: {error}"
        )


    # =====================================================
    # COPY BOT DATA
    # =====================================================

    for key in (
        "servers",
        "users",
        "channels",
        "latency",
        "commands",
        "verifications",
        "uptime",
        "last_seen",
        "updated_at",
    ):

        if key in bot_snapshot:

            statistics_data[key] = (
                bot_snapshot[key]
            )

    statistics_data["version"] = os.getenv(
        "MISUKI_VERSION",
        "1.0.0"
    )


    # =====================================================
    # HEARTBEAT
    # =====================================================

    current_time = time.time()

    last_seen = bot_snapshot.get(
        "last_seen"
    )


    if last_seen is not None:

        try:

            heartbeat_age = (
                current_time
                - float(last_seen)
            )


            if heartbeat_age <= 30:

                statistics_data[
                    "bot_status"
                ] = "Online"

            else:

                statistics_data[
                    "bot_status"
                ] = "Offline"


        except (
            TypeError,
            ValueError
        ):

            statistics_data[
                "bot_status"
            ] = "Offline"

    else:

        statistics_data[
            "bot_status"
        ] = "Offline"


    # =====================================================
    # API STATUS
    # =====================================================

    if statistics_data[
        "bot_status"
    ] == "Online":

        statistics_data[
            "api_status"
        ] = "Operational"

    else:

        statistics_data[
            "api_status"
        ] = "Unavailable"


    # =====================================================
    # TICKETS
    # =====================================================

    database_ok = True

    try:

        tickets_database = os.path.join(
            BASE_DIR,
            "data",
            "tickets.db"
        )


        with sqlite3.connect(
            tickets_database
        ) as connection:

            result = connection.execute(
                """
                SELECT
                    COALESCE(
                        SUM(number),
                        0
                    )
                FROM ticket_counter
                """
            ).fetchone()


            statistics_data[
                "tickets"
            ] = int(
                result[0] or 0
            )


    except (
        OSError,
        sqlite3.Error,
        TypeError,
        ValueError
    ):

        database_ok = False

        statistics_data[
            "tickets"
        ] = 0


    # =====================================================
    # MODERATION
    # =====================================================

    moderation_actions = 0

    try:

        moderation_database = os.path.join(
            BASE_DIR,
            "data",
            "moderation.db"
        )


        with sqlite3.connect(
            moderation_database
        ) as connection:

            result = connection.execute(
                """
                SELECT
                    COUNT(*)
                FROM warnings
                """
            ).fetchone()


            moderation_actions = int(
                result[0] or 0
            )


    except (
        OSError,
        sqlite3.Error,
        TypeError,
        ValueError
    ):

        database_ok = False

        moderation_actions = 0


    # =====================================================
    # DATABASE STATUS
    # =====================================================

    if database_ok:

        statistics_data[
            "database_status"
        ] = "Operational"

    else:

        statistics_data[
            "database_status"
        ] = "Error"


    # =====================================================
    # RESPONSE
    # =====================================================

    response = {

        "servers": statistics_data[
            "servers"
        ],

        "users": statistics_data[
            "users"
        ],

        "channels": statistics_data[
            "channels"
        ],

        "latency": statistics_data[
            "latency"
        ],

        "commands": statistics_data[
            "commands"
        ],

        "tickets": statistics_data[
            "tickets"
        ],

        "verifications": statistics_data[
            "verifications"
        ],

        "bot_status": statistics_data[
            "bot_status"
        ],

        "database_status": statistics_data[
            "database_status"
        ],

        "api_status": statistics_data[
            "api_status"
        ],

        "uptime": statistics_data[
            "uptime"
        ],

        "version": statistics_data[
            "version"
        ],

        "last_seen": statistics_data[
            "last_seen"
        ],

        "updated_at": statistics_data[
            "updated_at"
        ],
    }


    # =====================================================
    # ADMIN DATA
    # =====================================================

    if user_is_admin:

        response[
            "admin_servers"
        ] = bot_snapshot.get(
            "admin_servers",
            []
        )
        response[
            "admin_users"
        ] = get_admin_users(
            response.get(
                "admin_servers",
        []
    )
)
        response[
            "admin_statistics"
        ] = {

            "commands": statistics_data[
                "commands"
            ],

            "tickets": statistics_data[
                "tickets"
            ],

            "moderation": moderation_actions,

            "announcements": 0,
        }


    return jsonify(
        response
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
        user.get("id")
        or ""
    )

    if not user_id:

        return error_page(
            "❌ Review Error",
            "Your Discord account could not be identified.",
            400,
            user
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

        return redirect(
            "/login"
        )

    return render_template(
        "advertise.html",
        user=user,
        is_admin=is_admin,
        advertisement_prices={
            duration:
                f"{price:.2f}"
            for duration, price
            in ADVERTISEMENT_PRICES.items()
        }
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

        return redirect(
            "/login"
        )

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

    amount = ADVERTISEMENT_PRICES.get(
        duration
    )

    if amount is None:

        return error_page(
            "❌ Invalid price",
            "The selected advertisement price is invalid.",
            400,
            user
        )

    # -----------------------------------------------------
    # PAYPAL CONFIGURATION
    # -----------------------------------------------------

    if not paypal_is_configured():

        return error_page(
            "❌ Payment unavailable",
            "PayPal is not configured yet. Please try again later.",
            503,
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
        or ""
    )

    if not user_id:

        return error_page(
            "❌ Advertisement Error",
            "Your Discord account could not be identified.",
            400,
            user
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
    # CREATE PAYMENT RECORD
    # =====================================================

    payment_id = None

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
                        provider_order_id,
                        provider_capture_id,
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
                        NULL,
                        %s,
                        %s,
                        'pending',
                        %s,
                        %s
                    )
                    RETURNING id
                    """,
                    (
                        advertisement_id,
                        user_id,
                        amount,
                        PAYPAL_CURRENCY,
                        now,
                        now
                    )
                )

                payment_result = (
                    cursor.fetchone()
                )

                if not payment_result:

                    raise RuntimeError(
                        "Payment ID was not returned."
                    )

                payment_id = (
                    payment_result[0]
                )

            connection.commit()

    except Exception as error:

        print(
            f"❌ Advertisement payment record error: {error}"
        )

        return error_page(
            "❌ Payment Error",
            "The payment record could not be created.",
            500,
            user
        )

    # =====================================================
    # CREATE PAYPAL ORDER
    # =====================================================

    try:

        paypal_order = paypal_create_order(
            advertisement_id,
            title,
            duration,
            amount
        )

    except Exception as error:

        print(
            f"❌ PayPal order creation error: {error}"
        )

        update_payment_record(
            payment_id,
            "failed"
        )

        return error_page(
            "❌ Payment Error",
            "The PayPal payment could not be created. Please try again.",
            502,
            user
        )

    # =====================================================
    # SAVE PAYPAL ORDER
    # =====================================================

    updated = update_payment_record(
        payment_id,
        "pending",
        provider_order_id=paypal_order["id"],
        provider_payment_id=paypal_order["id"],
        amount=amount,
        currency=PAYPAL_CURRENCY
    )

    if not updated:

        print(
            "⚠️ PayPal order was created but payment record "
            "could not be updated."
        )

        return error_page(
            "❌ Payment Error",
            "The payment could not be prepared safely. Please contact support.",
            500,
            user
        )

    # =====================================================
    # SAVE PAYMENT CONTEXT
    # =====================================================

    session["pending_paypal_order_id"] = (
        paypal_order["id"]
    )

    session["pending_paypal_advertisement_id"] = (
        advertisement_id
    )

    session["pending_paypal_payment_id"] = (
        payment_id
    )

    session.permanent = True

    session.modified = True

    # =====================================================
    # REDIRECT TO PAYPAL
    # =====================================================

    return redirect(
        paypal_order["approval_url"]
    )


# =========================================================
# PAYPAL SUCCESS
# =========================================================

@app.route(
    "/advertise/paypal/success"
)
def paypal_success():

    user = get_user()

    if not user:

        return error_page(
            "❌ Payment Error",
            "Your login session expired. Please log in again.",
            401
        )

    order_id = request.args.get(
        "token"
    )

    if not order_id:

        return error_page(
            "❌ Payment Error",
            "PayPal did not return an order ID.",
            400,
            user
        )

    session_order_id = session.get(
        "pending_paypal_order_id"
    )

    if (
        session_order_id
        and
        str(session_order_id)
        != str(order_id)
    ):

        return error_page(
            "❌ Payment Error",
            "The PayPal order does not match the current payment.",
            400,
            user
        )

    advertisement_id = session.get(
        "pending_paypal_advertisement_id"
    )

    payment_id = session.get(
        "pending_paypal_payment_id"
    )

    if not advertisement_id or not payment_id:

        return error_page(
            "❌ Payment Error",
            "The payment session could not be verified.",
            400,
            user
        )

    # -----------------------------------------------------
    # VERIFY PAYMENT RECORD
    # -----------------------------------------------------

    payment = paypal_payment_status_for_ad(
        advertisement_id,
        str(
            user.get("id")
        )
    )

    if not payment:

        return error_page(
            "❌ Payment Error",
            "The payment record could not be found.",
            404,
            user
        )

    if int(
        payment["id"]
    ) != int(
        payment_id
    ):

        return error_page(
            "❌ Payment Error",
            "The payment session could not be verified.",
            400,
            user
        )

    stored_order_id = (
        payment.get(
            "provider_order_id"
        )
        or
        payment.get(
            "provider_payment_id"
        )
    )

    if (
        not stored_order_id
        or
        str(stored_order_id)
        != str(order_id)
    ):

        return error_page(
            "❌ Payment Error",
            "The PayPal order could not be verified.",
            400,
            user
        )

    # -----------------------------------------------------
    # ALREADY PAID
    # -----------------------------------------------------

    if str(
        payment.get(
            "status"
        )
        or
        ""
    ).lower() == "paid":

        session.pop(
            "pending_paypal_order_id",
            None
        )

        session.pop(
            "pending_paypal_advertisement_id",
            None
        )

        session.pop(
            "pending_paypal_payment_id",
            None
        )

        session.modified = True

        return render_template(
            "advertise_success.html",
            user=user,
            is_admin=is_admin
        )

    # -----------------------------------------------------
    # CAPTURE
    # -----------------------------------------------------

    try:

        paypal_response = paypal_capture_order(
            order_id
        )

    except Exception as error:

        print(
            f"❌ PayPal capture error: {error}"
        )

        return error_page(
            "❌ Payment Error",
            "PayPal could not complete the payment. Please try again.",
            502,
            user
        )

    paypal_status = str(
        paypal_response.get(
            "status",
            ""
        )
    ).upper()

    if paypal_status != "COMPLETED":

        print(
            "❌ PayPal payment was not completed:"
        )

        print(
            paypal_response
        )

        update_payment_record(
            payment_id,
            "failed"
        )

        return error_page(
            "❌ Payment not completed",
            "PayPal did not mark the payment as completed.",
            400,
            user
        )

    # -----------------------------------------------------
    # VERIFY PAYMENT AMOUNT
    # -----------------------------------------------------

    captured_amount, captured_currency = (
        paypal_extract_captured_amount(
            paypal_response
        )
    )

    stored_amount = payment.get(
        "amount"
    )

    try:

        stored_amount_decimal = Decimal(
            str(
                stored_amount
            )
        ).quantize(
            Decimal("0.01")
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError
    ):

        return error_page(
            "❌ Payment Error",
            "The stored payment amount is invalid.",
            500,
            user
        )

    if (
        captured_amount is None
        or
        captured_currency is None
    ):

        return error_page(
            "❌ Payment Error",
            "PayPal did not return a valid captured amount.",
            400,
            user
        )

    if captured_amount != stored_amount_decimal:

        print(
            "❌ PayPal amount mismatch:"
        )

        print(
            f"   Expected: {stored_amount_decimal}"
        )

        print(
            f"   Received: {captured_amount}"
        )

        update_payment_record(
            payment_id,
            "amount_mismatch"
        )

        return error_page(
            "❌ Payment Error",
            "The payment amount could not be verified.",
            400,
            user
        )

    if str(
        captured_currency
    ).upper() != str(
        PAYPAL_CURRENCY
    ).upper():

        print(
            "❌ PayPal currency mismatch:"
        )

        print(
            f"   Expected: {PAYPAL_CURRENCY}"
        )

        print(
            f"   Received: {captured_currency}"
        )

        update_payment_record(
            payment_id,
            "currency_mismatch"
        )

        return error_page(
            "❌ Payment Error",
            "The payment currency could not be verified.",
            400,
            user
        )

    # -----------------------------------------------------
    # CAPTURE ID
    # -----------------------------------------------------

    capture_id = paypal_extract_capture_id(
        paypal_response
    )

    # -----------------------------------------------------
    # MARK PAID
    # -----------------------------------------------------

    updated = update_payment_record(
        payment_id,
        "paid",
        provider_order_id=order_id,
        provider_capture_id=capture_id,
        provider_payment_id=(
            capture_id
            or
            order_id
        ),
        amount=captured_amount,
        currency=captured_currency
    )

    if not updated:

        return error_page(
            "❌ Payment Error",
            "The payment was completed but could not be saved. Please contact support.",
            500,
            user
        )

    # -----------------------------------------------------
    # CLEAR PAYMENT SESSION
    # -----------------------------------------------------

    session.pop(
        "pending_paypal_order_id",
        None
    )

    session.pop(
        "pending_paypal_advertisement_id",
        None
    )

    session.pop(
        "pending_paypal_payment_id",
        None
    )

    session.modified = True

    # -----------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------

    return render_template(
        "advertise_success.html",
        user=user,
        is_admin=is_admin
    )


# =========================================================
# PAYPAL CANCEL
# =========================================================

@app.route(
    "/advertise/paypal/cancel"
)
def paypal_cancel():

    user = get_user()

    advertisement_id = session.get(
        "pending_paypal_advertisement_id"
    )

    payment_id = session.get(
        "pending_paypal_payment_id"
    )

    if payment_id:

        update_payment_record(
            payment_id,
            "cancelled"
        )

    if (
        advertisement_id
        and
        DATABASE_URL
    ):

        try:

            with database_connection() as connection:

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        UPDATE advertisements
                        SET
                            status = 'cancelled',
                            updated_at = %s
                        WHERE id = %s
                        AND status = 'pending'
                        """,
                        (
                            utc_now().isoformat(),
                            advertisement_id
                        )
                    )

                connection.commit()

        except Exception as error:

            print(
                f"⚠️ Could not cancel advertisement: {error}"
            )

    session.pop(
        "pending_paypal_order_id",
        None
    )

    session.pop(
        "pending_paypal_advertisement_id",
        None
    )

    session.pop(
        "pending_paypal_payment_id",
        None
    )

    session.modified = True

    if not user:

        return redirect(
            "/"
        )

    return error_page(
        "Payment cancelled",
        "The PayPal payment was cancelled. The advertisement was not submitted.",
        400,
        user
    )


# =========================================================
# ADMIN ADVERTISEMENT PANEL
# =========================================================

@app.route(
    "/admin/advertise"
)
def admin_advertisements():

    user = get_user()

    if not user:

        session["next_url"] = (
            "/admin/advertise"
        )

        return redirect(
            "/login"
        )

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
        "admin_advertise.html",
        user=user,
        advertisements=advertisements,
        is_admin=is_admin
    )


# =========================================================
# ADMIN APPROVE ADVERTISEMENT
# =========================================================

@app.route(
    "/admin/advertise/<int:advertisement_id>/approve",
    methods=["POST"]
)
def approve_advertisement(
    advertisement_id
):

    user = get_user()

    if not user:

        session["next_url"] = (
            "/admin/advertise"
        )

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
                        user_id,
                        duration_days,
                        status
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
    # PAYMENT VERIFICATION
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
                        amount,
                        currency,
                        status,
                        provider,
                        provider_order_id,
                        provider_capture_id
                    FROM advertisement_payments
                    WHERE advertisement_id = %s
                    AND provider = 'paypal'
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (
                        advertisement_id,
                    )
                )

                payment = cursor.fetchone()

    except Exception as error:

        print(
            f"❌ Advertisement payment lookup error: {error}"
        )

        return error_page(
            "❌ Payment Error",
            "The advertisement payment could not be verified.",
            500,
            user
        )

    if not payment:

        return error_page(
            "❌ Payment required",
            "This advertisement has no PayPal payment record.",
            402,
            user
        )

    if str(
        payment.get(
            "status",
            ""
        )
    ).lower() != "paid":

        return error_page(
            "❌ Payment required",
            "This advertisement cannot be approved until the PayPal payment is completed.",
            402,
            user
        )

    # -----------------------------------------------------
    # VERIFY STORED PRICE
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

        return error_page(
            "❌ Advertisement Error",
            "The advertisement duration is invalid.",
            400,
            user
        )

    expected_amount = (
        ADVERTISEMENT_PRICES.get(
            duration_days
        )
    )

    if expected_amount is None:

        return error_page(
            "❌ Advertisement Error",
            "The advertisement duration has an invalid price.",
            400,
            user
        )

    try:

        paid_amount = Decimal(
            str(
                payment.get(
                    "amount"
                )
            )
        ).quantize(
            Decimal("0.01")
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError
    ):

        return error_page(
            "❌ Payment Error",
            "The stored payment amount is invalid.",
            500,
            user
        )

    if paid_amount != expected_amount:

        return error_page(
            "❌ Payment Error",
            "The payment amount does not match the advertisement duration.",
            400,
            user
        )

    if str(
        payment.get(
            "currency"
        )
        or
        ""
    ).upper() != PAYPAL_CURRENCY:

        return error_page(
            "❌ Payment Error",
            "The payment currency is invalid.",
            400,
            user
        )

    # -----------------------------------------------------
    # PREVENT RE-APPROVAL
    # -----------------------------------------------------

    if str(
        advertisement.get(
            "status"
        )
        or
        ""
    ).lower() == "active":

        return redirect(
            "/admin/advertise"
        )

    # -----------------------------------------------------
    # CALCULATE START AND END
    # -----------------------------------------------------

    start_at = now

    end_at = (
        start_at
        +
        timedelta(
            days=duration_days
        )
    )

    print(
        "📢 Advertisement approved:"
    )

    print(
        f"   ID: {advertisement_id}"
    )

    print(
        f"   Duration: {duration_days} days"
    )

    print(
        f"   Paid: €{paid_amount:.2f}"
    )

    print(
        f"   Start: {start_at.isoformat()}"
    )

    print(
        f"   End: {end_at.isoformat()}"
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
        "/admin/advertise"
    )


# =========================================================
# ADMIN REJECT ADVERTISEMENT
# =========================================================

@app.route(
    "/admin/advertise/<int:advertisement_id>/reject",
    methods=["POST"]
)
def reject_advertisement(
    advertisement_id
):

    user = get_user()

    if not user:

        session["next_url"] = (
            "/admin/advertise"
        )

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
        "/admin/advertise"
    )


# =========================================================
# ADMIN DISABLE ADVERTISEMENT
# =========================================================

@app.route(
    "/admin/advertise/<int:advertisement_id>/disable",
    methods=["POST"]
)
def disable_advertisement(
    advertisement_id
):

    user = get_user()

    if not user:

        session["next_url"] = (
            "/admin/advertise"
        )

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
        "/admin/advertise"
    )


# =========================================================
# DOCUMENTATION
# =========================================================

@app.route(
    "/documentation"
)
def documentation():

    user = get_user()

    return render_template(
        "documentation.html",
        user=user,
        is_admin=is_admin
    )


# =========================================================
# SUPPORT
# =========================================================

@app.route(
    "/support"
)
def support():

    user = get_user()

    return render_template(
        "support.html",
        user=user,
        is_admin=is_admin
    )


# =========================================================
# TERMS
# =========================================================

@app.route(
    "/terms"
)
def terms():

    user = get_user()

    return render_template(
        "terms.html",
        user=user,
        is_admin=is_admin
    )


# =========================================================
# PRIVACY
# =========================================================

@app.route(
    "/privacy"
)
def privacy():

    user = get_user()

    return render_template(
        "privacy.html",
        user=user,
        is_admin=is_admin
    )


# =========================================================
# DATA
# =========================================================

@app.route(
    "/data"
)
def data_page():

    user = get_user()

    return render_template(
        "data.html",
        user=user,
        is_admin=is_admin
    )


# =========================================================
# COOKIES
# =========================================================

@app.route(
    "/cookies"
)
def cookies_page():

    user = get_user()

    return render_template(
        "cookies.html",
        user=user,
        is_admin=is_admin
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
        ),

        "login_redirect": bool(
            DISCORD_LOGIN_REDIRECT_URI
        ),

        "paypal": paypal_is_configured(),

        "paypal_mode": PAYPAL_MODE,

        "paypal_currency": PAYPAL_CURRENCY
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
        f"🔐 Login Redirect configured: "
        f"{bool(DISCORD_LOGIN_REDIRECT_URI)}"
    )

    print(
        f"💳 PayPal Client ID configured: "
        f"{bool(PAYPAL_CLIENT_ID)}"
    )

    print(
        f"💳 PayPal Client Secret configured: "
        f"{bool(PAYPAL_CLIENT_SECRET)}"
    )

    print(
        f"💳 PayPal Mode: "
        f"{PAYPAL_MODE}"
    )

    print(
        f"💶 PayPal Currency: "
        f"{PAYPAL_CURRENCY}"
    )

    print(
        f"💰 Advertisement Prices: "
        f"7d €{ADVERTISEMENT_PRICES[7]:.2f} | "
        f"14d €{ADVERTISEMENT_PRICES[14]:.2f} | "
        f"30d €{ADVERTISEMENT_PRICES[30]:.2f}"
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
