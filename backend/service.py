"""Business rules — sits between the API layer and the repository."""

from fastapi import HTTPException
from psycopg.errors import ForeignKeyViolation, UniqueViolation

import repository
from models import ReviewCreate


def list_employees() -> list[dict]:
    return repository.get_all_employees()


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
