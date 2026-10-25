"""Business rules — sits between the API layer and the repository."""

import repository


def list_employees() -> list[dict]:
    return repository.get_all_employees()

def list_reviews(
    employee_id: int | None = None,
    period_id: int | None = None
) -> list[dict]:
    return repository.get_all_reviews(
        employee_id=employee_id,
        period_id=period_id
    )


def get_review(review_id: int) -> dict | None:
    return repository.get_review_by_id(review_id)


def create_review(review_data: dict) -> dict:
    return repository.create_review(review_data)
