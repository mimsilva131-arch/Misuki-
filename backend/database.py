
# =========================================================
# MISUKI - DATABASE
# =========================================================

import os
import sqlite3


# =========================================================
# PATH
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
# DATABASE INITIALIZATION
# =========================================================

def init_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            discord_id TEXT UNIQUE NOT NULL,

            username TEXT,

            avatar TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
        """
    )

    connection.commit()

    connection.close()


# =========================================================
# USER
# =========================================================

def get_user(
    discord_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *

        FROM users

        WHERE discord_id = ?
        """,
        (
            str(discord_id),
        )
    )

    user = cursor.fetchone()

    connection.close()

    return user


def save_user(
    discord_id,
    username=None,
    avatar=None
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO users
        (
            discord_id,
            username,
            avatar
        )

        VALUES (?, ?, ?)

        ON CONFLICT(discord_id)

        DO UPDATE SET

            username = excluded.username,

            avatar = excluded.avatar
        """,
        (
            str(discord_id),
            username,
            avatar
        )
    )

    connection.commit()

    connection.close()


# =========================================================
# STARTUP
# =========================================================

init_database()

