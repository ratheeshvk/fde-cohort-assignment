"""Business rules — sits between the API layer and the repository."""

from fastapi import HTTPException
from psycopg.errors import ForeignKeyViolation, UniqueViolation

import repository
from models import ReviewCreate


def list_employees() -> list[dict]:
    return repository.get_all_employees()


def list_reviews(
    employee_id: int | None = None,
    period_id: int | None = None,
) -> list[dict]:
    return repository.get_all_reviews(
        employee_id=employee_id,
        period_id=period_id,
    )


def get_review(review_id: int) -> dict | None:
    return repository.get_review_by_id(review_id)


def create_review(review: ReviewCreate) -> dict:
    try:
        return repository.create_review(review)
    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="A review already exists for this employee and period",
        ) from None
    except ForeignKeyViolation as exc:
        constraint = exc.diag.constraint_name if exc.diag else None
        if constraint == "performance_reviews_period_id_fkey":
            detail = "Review period not found"
        else:
            detail = "Employee not found"
        raise HTTPException(status_code=404, detail=detail) from None

def get_employee(employee_code: str) -> dict | None:
        # Business rule: codes are stored uppercase (EMP101), so accept emp101 too
        employee_code = employee_code.strip().upper()
        return repository.get_employee_by_code(employee_code)