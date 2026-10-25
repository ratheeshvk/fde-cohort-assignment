"""Shared fixtures. The repository is always mocked, so no database is required."""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from psycopg.errors import ForeignKeyViolation

from main import app


class _ForeignKeyError(ForeignKeyViolation):
    # psycopg's `diag` is read-only, so a subclass is the only way to fake a constraint name.
    def __init__(self, constraint_name: str):
        super().__init__("foreign key violation")
        self._constraint_name = constraint_name

    @property
    def diag(self):
        return type("Diag", (), {"constraint_name": self._constraint_name})()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def employee():
    return {
        "id": 1,
        "employee_id": "EMP101",
        "name": "Ada Lovelace",
        "department": "Engineering",
        "email": "ada@example.com",
        "status": "active",
    }


@pytest.fixture
def review():
    return {
        "id": 10,
        "employee_id": 1,
        "employee_name": "Ada Lovelace",
        "period_id": 2,
        "period_name": "2026 Q1",
        "quality_rating": 4,
        "delivery_rating": 5,
        "teamwork_rating": 3,
        "average_rating": 4.0,
        "comments": "Strong quarter",
        "created_at": datetime(2026, 1, 15, tzinfo=timezone.utc),
    }


@pytest.fixture
def create_body():
    return {
        "employee_id": 1,
        "period_id": 2,
        "quality_rating": 4,
        "delivery_rating": 5,
        "teamwork_rating": 3,
        "comments": "Strong quarter",
    }


@pytest.fixture
def foreign_key_error():
    return _ForeignKeyError
