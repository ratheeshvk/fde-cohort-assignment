"""Create the admins table and the first admin from ADMIN_USERNAME / ADMIN_PASSWORD in .env.

There is no sign-up endpoint; run this once (it is safe to re-run):
    python init_db.py
"""

import os

from database import get_connection
from service import hash_password

CREATE_ADMINS = """
CREATE TABLE IF NOT EXISTS admins (
    id             SERIAL       PRIMARY KEY,
    username       VARCHAR(50)  NOT NULL UNIQUE,
    password_hash  TEXT         NOT NULL,
    created_at     TIMESTAMP    DEFAULT NOW()
)
"""


def main() -> None:
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    if not username or not password:
        raise SystemExit("Set ADMIN_USERNAME and ADMIN_PASSWORD in .env first.")

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(CREATE_ADMINS)
            # Only the hash is stored. An existing admin is left untouched, so re-running never resets a password.
            cursor.execute(
                """
                INSERT INTO admins (username, password_hash)
                VALUES (%s, %s)
                ON CONFLICT (username) DO NOTHING
                """,
                (username, hash_password(password)),
            )
            created = cursor.rowcount == 1
        conn.commit()

    print(f"Admin '{username}' {'created' if created else 'already exists, left unchanged'}.")


if __name__ == "__main__":
    main()
