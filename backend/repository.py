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
