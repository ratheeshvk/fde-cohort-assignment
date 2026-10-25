"""Database connection helpers."""

import os
from pathlib import Path

from dotenv import load_dotenv
from psycopg import connect

# The .env file lives at the repository root, one level above backend/.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def get_connection():
    """Return a PostgreSQL connection using DATABASE_URL from .env."""
    database_url = os.getenv("DATABASE_URL")
    if database_url is None:
        raise RuntimeError("DATABASE_URL is not set")
    return connect(database_url)


if __name__ == "__main__":
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database(), version()")
            db_name, version = cursor.fetchone()
            print(f"Connected to {db_name}: {version}")
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
                """
            )
            print("Tables:", [row[0] for row in cursor.fetchall()])
