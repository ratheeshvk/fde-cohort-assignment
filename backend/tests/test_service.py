"""Service-layer tests: business rules, called directly without HTTP."""

from unittest.mock import patch

import pytest
from fastapi import HTTPException
from psycopg.errors import UniqueViolation

import service
from models import ReviewCreate


def test_list_employees_returns_repository_rows(employee):
    with patch("repository.get_all_employees", return_value=[employee]):
        assert service.list_employees() == [employee]


@pytest.mark.parametrize("raw_code", ["EMP101", "emp101", "  Emp101  "])
def test_get_employee_normalizes_code(employee, raw_code):
    with patch("repository.get_employee_by_code", return_value=employee) as get_employee:
        assert service.get_employee(raw_code) == employee

    get_employee.assert_called_once_with("EMP101")


def test_get_employee_returns_none_when_missing():
    with patch("repository.get_employee_by_code", return_value=None):
        assert service.get_employee("EMP999") is None


def test_list_reviews_passes_filters(review):
    with patch("repository.get_all_reviews", return_value=[review]) as get_reviews:
        assert service.list_reviews(employee_id=1, period_id=2) == [review]

    get_reviews.assert_called_once_with(employee_id=1, period_id=2)


def test_list_reviews_defaults_to_no_filters():
    with patch("repository.get_all_reviews", return_value=[]) as get_reviews:
        assert service.list_reviews() == []

    get_reviews.assert_called_once_with(employee_id=None, period_id=None)


def test_get_review(review):
    with patch("repository.get_review_by_id", return_value=review) as get_review:
        assert service.get_review(10) == review

    get_review.assert_called_once_with(10)


def test_get_review_returns_none_when_missing():
    with patch("repository.get_review_by_id", return_value=None):
        assert service.get_review(99) is None


def test_create_review_returns_saved_row(review, create_body):
    payload = ReviewCreate(**create_body)
    with patch("repository.create_review", return_value=review) as create_review:
        assert service.create_review(payload) == review

    create_review.assert_called_once_with(payload)


def test_create_review_duplicate_raises_409(create_body):
    with patch("repository.create_review", side_effect=UniqueViolation("duplicate")):
        with pytest.raises(HTTPException) as exc_info:
            service.create_review(ReviewCreate(**create_body))

    assert exc_info.value.status_code == 409


@pytest.mark.parametrize(
    ("constraint", "detail"),
    [
        ("performance_reviews_employee_id_fkey", "Employee not found"),
        ("performance_reviews_period_id_fkey", "Review period not found"),
        (None, "Employee not found"),
    ],
)
def test_create_review_foreign_key_raises_404(create_body, foreign_key_error, constraint, detail):
    with patch("repository.create_review", side_effect=foreign_key_error(constraint)):
        with pytest.raises(HTTPException) as exc_info:
            service.create_review(ReviewCreate(**create_body))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == detail


def test_create_review_lets_unexpected_errors_propagate(create_body):
    with patch("repository.create_review", side_effect=RuntimeError("boom")):
        with pytest.raises(RuntimeError):
            service.create_review(ReviewCreate(**create_body))
