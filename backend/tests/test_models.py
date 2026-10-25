"""Pydantic model validation tests."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from models import Employee, Review, ReviewCreate

RATING_FIELDS = ["quality_rating", "delivery_rating", "teamwork_rating"]


@pytest.mark.parametrize("field", RATING_FIELDS)
@pytest.mark.parametrize("value", [1, 5])
def test_review_create_accepts_boundary_ratings(create_body, field, value):
    review = ReviewCreate(**{**create_body, field: value})

    assert getattr(review, field) == value


@pytest.mark.parametrize("field", RATING_FIELDS)
@pytest.mark.parametrize("value", [0, 6, -1])
def test_review_create_rejects_out_of_range_ratings(create_body, field, value):
    with pytest.raises(ValidationError):
        ReviewCreate(**{**create_body, field: value})


@pytest.mark.parametrize("field", ["employee_id", "period_id", *RATING_FIELDS])
def test_review_create_requires_field(create_body, field):
    body = {key: value for key, value in create_body.items() if key != field}

    with pytest.raises(ValidationError):
        ReviewCreate(**body)


def test_review_create_comments_optional(create_body):
    body = {key: value for key, value in create_body.items() if key != "comments"}

    assert ReviewCreate(**body).comments is None


def test_review_create_rejects_non_numeric_rating(create_body):
    with pytest.raises(ValidationError):
        ReviewCreate(**{**create_body, "quality_rating": "great"})


def test_review_accepts_row_without_joined_names(review):
    row = {key: value for key, value in review.items() if key not in ("employee_name", "period_name")}

    parsed = Review(**row)

    assert parsed.employee_name is None
    assert parsed.period_name is None


def test_review_coerces_decimal_average(review):
    parsed = Review(**{**review, "average_rating": Decimal("3.67")})

    assert parsed.average_rating == pytest.approx(3.67)


def test_employee_optional_fields_default_to_none():
    employee = Employee(id=1, employee_id="EMP101", name="Ada Lovelace")

    assert employee.department is None
    assert employee.email is None
    assert employee.status is None


def test_employee_requires_name():
    with pytest.raises(ValidationError):
        Employee(id=1, employee_id="EMP101")
