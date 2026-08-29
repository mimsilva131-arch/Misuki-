
# =========================================================
# MISUKI - LICENSES
# =========================================================

import os
import sqlite3


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

os.makedirs(
    DATA_DIR,
    exist_ok=True
)

DATABASE = os.path.join(
    DATA_DIR,
    "misuki.db"
)


# =========================================================
# CONNECTION
# =========================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# DATABASE SETUP
# =========================================================

def init_licenses():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS licenses (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            guild_id TEXT UNIQUE NOT NULL,

            license_key TEXT UNIQUE NOT NULL,

            active BOOLEAN NOT NULL
                DEFAULT TRUE,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
        """
    )

    connection.commit()

    connection.close()


# =========================================================
# GET LICENSE
# =========================================================

def get_license(guild_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM licenses
        WHERE guild_id = ?
        """,
        (
            str(guild_id),
        )
    )

    license_data = cursor.fetchone()

    connection.close()

    return license_data


# =========================================================
# CHECK LICENSE
# =========================================================

def has_active_license(guild_id):

    license_data = get_license(
        guild_id
    )

    if license_data is None:

        return False

    # -----------------------------------------------------
    # Get available columns safely
    # -----------------------------------------------------

    try:

        columns = license_data.keys()

    except AttributeError:

        return False

    # -----------------------------------------------------
    # Active column exists
    # -----------------------------------------------------

    if "active" in columns:

        try:

            return bool(
                license_data["active"]
            )

        except (
            KeyError,
            IndexError
        ):

            return False

    # -----------------------------------------------------
    # Compatibility with old databases
    # -----------------------------------------------------

    if "status" in columns:

        try:

            return str(
                license_data["status"]
            ).lower() == "active"

        except (
            KeyError,
            IndexError
        ):

            return False

    # -----------------------------------------------------
    # No known status column
    # -----------------------------------------------------

    return False


# =========================================================
# CREATE LICENSE
# =========================================================

def create_license(
    guild_id,
    license_key
):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO licenses
            (
                guild_id,
                license_key,
                active
            )

            VALUES (?, ?, TRUE)
            """,
            (
                str(guild_id),
                license_key
            )
        )

        connection.commit()

    finally:

        connection.close()


# =========================================================
# DISABLE LICENSE
# =========================================================

def disable_license(guild_id):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE licenses

            SET active = FALSE

            WHERE guild_id = ?
            """,
            (
                str(guild_id),
            )
        )

        connection.commit()

    finally:

        connection.close()


# =========================================================
# ENABLE LICENSE
# =========================================================

def enable_license(guild_id):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE licenses

            SET active = TRUE

            WHERE guild_id = ?
            """,
            (
                str(guild_id),
            )
        )

        connection.commit()

    finally:

        connection.close()


# =========================================================
# DELETE LICENSE
# =========================================================

def delete_license(guild_id):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM licenses

            WHERE guild_id = ?
            """,
            (
                str(guild_id),
            )
        )

        connection.commit()

    finally:

        connection.close()


# =========================================================
# GET ALL LICENSES
# =========================================================

def get_all_licenses():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM licenses
        ORDER BY id DESC
        """
    )

    licenses = cursor.fetchall()

    connection.close()

    return licenses


# =========================================================
# STARTUP
# =========================================================

init_licenses()

