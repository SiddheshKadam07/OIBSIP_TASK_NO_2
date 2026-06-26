# ============================================================
#  database.py  –  SQLite Storage for BMI Records
# ============================================================

import sqlite3
import datetime
import os

# Database file lives next to this script
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bmi_data.db")


def init_db() -> None:
    """Create the database and table if they don't already exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                user     TEXT    NOT NULL,
                weight   REAL    NOT NULL,
                height   REAL    NOT NULL,
                bmi      REAL    NOT NULL,
                category TEXT    NOT NULL,
                date     TEXT    NOT NULL
            )
        """)
        conn.commit()


def save_record(user: str, weight: float, height: float,
                bmi: float, category: str) -> None:
    """Insert a new BMI record for the given user."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO bmi_records "
            "(user, weight, height, bmi, category, date) VALUES (?,?,?,?,?,?)",
            (user, weight, height, bmi, category, timestamp),
        )
        conn.commit()


def get_all_users() -> list[str]:
    """Return a sorted list of all distinct user names."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT DISTINCT user FROM bmi_records ORDER BY user"
        ).fetchall()
    return [r[0] for r in rows]


def get_records_for_user(user: str) -> list[tuple]:
    """Return all records for a specific user, sorted by date ascending."""
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT * FROM bmi_records WHERE user=? ORDER BY date ASC",
            (user,)
        ).fetchall()


def get_all_records(limit: int = 200) -> list[tuple]:
    """Return the most recent records across all users."""
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT * FROM bmi_records ORDER BY date DESC LIMIT ?",
            (limit,)
        ).fetchall()


def delete_all_records() -> None:
    """Permanently remove every record from the database."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM bmi_records")
        conn.commit()


def delete_user_records(user: str) -> None:
    """Remove all records for a specific user."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM bmi_records WHERE user=?", (user,))
        conn.commit()
