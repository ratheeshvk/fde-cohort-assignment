"""Data access layer — SQL queries live here."""

from psycopg.rows import dict_row

from database import get_connection
from models import ReviewCreate

def get_all_employees() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT id, employee_id, name, department, email, status
                FROM employees
                ORDER BY id
                """
            )
            return cursor.fetchall()


def get_all_review_periods() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT id, name, start_date, end_date, status
                FROM review_periods
                ORDER BY id
                """
            )
            return cursor.fetchall()


def create_review(review: ReviewCreate) -> dict:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO performance_reviews (
                    employee_id,
                    period_id,
                    quality_rating,
                    delivery_rating,
                    teamwork_rating,
                    comments
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING
                    id,
                    employee_id,
                    period_id,
                    quality_rating,
                    delivery_rating,
                    teamwork_rating,
                    average_rating,
                    comments,
                    created_at
                """,
                (
                    review.employee_id,
                    review.period_id,
                    review.quality_rating,
                    review.delivery_rating,
                    review.teamwork_rating,
                    review.comments,
                ),
            )
            row = cursor.fetchone()
            if row is None:
                raise RuntimeError("Insert did not return a review")
            conn.commit()
            return row


def get_all_reviews(
    employee_id: int | None = None,
    period_id: int | None = None,
) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            query = """
                SELECT
                    pr.id,
                    pr.employee_id,
                    e.name AS employee_name,
                    pr.period_id,
                    rp.name AS period_name,
                    pr.quality_rating,
                    pr.delivery_rating,
                    pr.teamwork_rating,
                    pr.average_rating,
                    pr.comments,
                    pr.created_at
                FROM performance_reviews pr
                JOIN employees e
                    ON pr.employee_id = e.id
                JOIN review_periods rp
                    ON pr.period_id = rp.id
                WHERE 1 = 1
            """
            params: list[int] = []
            if employee_id is not None:
                query += " AND pr.employee_id = %s"
                params.append(employee_id)
            if period_id is not None:
                query += " AND pr.period_id = %s"
                params.append(period_id)
            query += " ORDER BY pr.id"
            cursor.execute(query, params)
            return cursor.fetchall()


def get_review_by_id(review_id: int) -> dict | None:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    pr.id,
                    pr.employee_id,
                    e.name AS employee_name,
                    pr.period_id,
                    rp.name AS period_name,
                    pr.quality_rating,
                    pr.delivery_rating,
                    pr.teamwork_rating,
                    pr.average_rating,
                    pr.comments,
                    pr.created_at
                FROM performance_reviews pr
                JOIN employees e
                    ON pr.employee_id = e.id
                JOIN review_periods rp
                    ON pr.period_id = rp.id
                WHERE pr.id = %s
                """,
                (review_id,),
            )
            return cursor.fetchone()


def get_employee_by_code(employee_code: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT id, employee_id, name, department, email, status
                    FROM employees
                    WHERE employee_id = %s
                    """,
                    (employee_code,),
                )
                return cursor.fetchone()

def fetch_admin_by_username(username: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT id, username, password_hash
                FROM admins
                WHERE username = %s
                """,
                (username,),
            )
            return cursor.fetchone()
