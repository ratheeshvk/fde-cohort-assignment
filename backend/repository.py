"""Data access layer — SQL queries live here."""

from psycopg.rows import dict_row

from database import get_connection
from models import TaskCreate


def get_all_tasks() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT id, title, description, status, created_at
                FROM tasks
                ORDER BY id
                """
            )
            return cursor.fetchall()


def create_task(task: TaskCreate) -> dict:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO tasks (title, description, status)
                VALUES (%s, %s, %s)
                RETURNING id, title, description, status, created_at
                """,
                (task.title, task.description, task.status),
            )
            row = cursor.fetchone()
            if row is None:
                raise RuntimeError("Insert did not return a task")
            conn.commit()
            return row


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
