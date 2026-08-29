
# =========================================================
# MISUKI - REVIEWS
# =========================================================

import os
import sqlite3


# =========================================================
# DATABASE
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

def init_reviews():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            discord_id TEXT,

            username TEXT NOT NULL,

            rating INTEGER NOT NULL,

            content TEXT NOT NULL,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
        """
    )

    connection.commit()

    connection.close()


# =========================================================
# ADD REVIEW
# =========================================================

def add_review(
    username,
    rating,
    content,
    discord_id=None
):

    if not username:
        return False

    if not content:
        return False

    try:
        rating = int(rating)

    except (
        TypeError,
        ValueError
    ):

        return False

    if rating < 1 or rating > 5:

        return False

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO reviews
        (
            discord_id,
            username,
            rating,
            content
        )

        VALUES (?, ?, ?, ?)
        """,
        (
            discord_id,
            username,
            rating,
            content
        )
    )

    connection.commit()

    connection.close()

    return True


# =========================================================
# GET REVIEWS
# =========================================================

def get_reviews():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *

        FROM reviews

        ORDER BY created_at DESC
        """
    )

    reviews = cursor.fetchall()

    connection.close()

    return reviews


# =========================================================
# GET REVIEW
# =========================================================

def get_review(
    review_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *

        FROM reviews

        WHERE id = ?
        """,
        (
            review_id,
        )
    )

    review = cursor.fetchone()

    connection.close()

    return review


# =========================================================
# DELETE REVIEW
# =========================================================

def delete_review(
    review_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM reviews

        WHERE id = ?
        """,
        (
            review_id,
        )
    )

    deleted = cursor.rowcount

    connection.commit()

    connection.close()

    return deleted > 0


# =========================================================
# STARTUP
# =========================================================

init_reviews()

