"""HTTP API tests: status codes, response shapes, validation, and error mapping."""

from unittest.mock import patch

import pytest
from psycopg.errors import UniqueViolation


def test_list_employees(client, employee):
    with patch("repository.get_all_employees", return_value=[employee]):
        response = client.get("/employees")

    assert response.status_code == 200
    assert response.json() == [employee]


def test_list_employees_empty(client):
    with patch("repository.get_all_employees", return_value=[]):
        response = client.get("/employees")

    assert response.status_code == 200
    assert response.json() == []


def test_get_employee_normalizes_code(client, employee):
    with patch("repository.get_employee_by_code", return_value=employee) as get_employee:
        response = client.get("/employees/ emp101 ")

    assert response.status_code == 200
    assert response.json()["employee_id"] == "EMP101"
    get_employee.assert_called_once_with("EMP101")


def test_get_employee_not_found(client):
    with patch("repository.get_employee_by_code", return_value=None):
        response = client.get("/employees/EMP999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


def test_get_employee_code_too_long(client):
    response = client.get("/employees/" + ("A" * 21))

    assert response.status_code == 422


def test_list_review_periods(client, review_period):
    with patch("repository.get_all_review_periods", return_value=[review_period]):
        response = client.get("/review-periods")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "H1-2026",
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "status": "Open",
        }
    ]


def test_list_review_periods_empty(client):
    with patch("repository.get_all_review_periods", return_value=[]):
        response = client.get("/review-periods")

    assert response.status_code == 200
    assert response.json() == []


def test_list_reviews(client, review):
    with patch("repository.get_all_reviews", return_value=[review]) as get_reviews:
        response = client.get("/reviews")

    assert response.status_code == 200
    body = response.json()
    assert body[0]["id"] == 10
    assert body[0]["employee_name"] == "Ada Lovelace"
    assert body[0]["average_rating"] == 4.0
    get_reviews.assert_called_once_with(employee_id=None, period_id=None)


def test_list_reviews_empty(client):
    with patch("repository.get_all_reviews", return_value=[]):
        response = client.get("/reviews")

    assert response.status_code == 200
    assert response.json() == []


def test_list_reviews_filters_by_employee_and_period(client, review):
    with patch("repository.get_all_reviews", return_value=[review]) as get_reviews:
        response = client.get("/reviews", params={"employee_id": 1, "period_id": 2})

    assert response.status_code == 200
    get_reviews.assert_called_once_with(employee_id=1, period_id=2)


def test_list_reviews_rejects_invalid_filter(client):
    response = client.get("/reviews", params={"employee_id": "abc"})

    assert response.status_code == 422


def test_get_review(client, review):
    with patch("repository.get_review_by_id", return_value=review):
        response = client.get("/reviews/10")

    assert response.status_code == 200
    assert response.json()["period_name"] == "2026 Q1"


def test_get_review_not_found(client):
    with patch("repository.get_review_by_id", return_value=None):
        response = client.get("/reviews/99")

    assert response.status_code == 404
    assert response.json()["detail"] == "Review not found"


def test_get_review_rejects_non_numeric_id(client):
    response = client.get("/reviews/abc")

    assert response.status_code == 422


def test_create_review(client, review, create_body):
    with patch("repository.create_review", return_value=review) as create_review:
        response = client.post("/api/reviews", json=create_body)

    assert response.status_code == 201
    assert response.json()["id"] == 10
    create_review.assert_called_once()
    saved = create_review.call_args.args[0]
    assert saved.employee_id == 1
    assert saved.period_id == 2
    assert saved.comments == "Strong quarter"


def test_create_review_without_comments(client, review, create_body):
    body = {key: value for key, value in create_body.items() if key != "comments"}
    with patch("repository.create_review", return_value={**review, "comments": None}) as create_review:
        response = client.post("/api/reviews", json=body)

    assert response.status_code == 201
    assert response.json()["comments"] is None
    assert create_review.call_args.args[0].comments is None


def test_create_review_duplicate(client, create_body):
    with patch("repository.create_review", side_effect=UniqueViolation("duplicate")):
        response = client.post("/api/reviews", json=create_body)

    assert response.status_code == 409
    assert response.json()["detail"] == "A review already exists for this employee and period"


@pytest.mark.parametrize(
    ("constraint", "detail"),
    [
        ("performance_reviews_employee_id_fkey", "Employee not found"),
        ("performance_reviews_period_id_fkey", "Review period not found"),
    ],
)
def test_create_review_missing_reference(client, create_body, foreign_key_error, constraint, detail):
    with patch("repository.create_review", side_effect=foreign_key_error(constraint)):
        response = client.post("/api/reviews", json=create_body)

    assert response.status_code == 404
    assert response.json()["detail"] == detail


def test_create_review_rejects_rating_out_of_range(client, create_body):
    response = client.post("/api/reviews", json={**create_body, "quality_rating": 6})

    assert response.status_code == 422


def test_create_review_rejects_missing_fields(client):
    response = client.post("/api/reviews", json={"employee_id": 1})

    assert response.status_code == 422
