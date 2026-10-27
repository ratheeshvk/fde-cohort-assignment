"""Shared fixtures. The repository is always mocked, so no database is required."""

from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from psycopg.errors import ForeignKeyViolation

from main import app, require_admin
from models import AdminUser


class _ForeignKeyError(ForeignKeyViolation):
    # psycopg's `diag` is read-only, so a subclass is the only way to fake a constraint name.
    def __init__(self, constraint_name: str):
        super().__init__("foreign key violation")
        self._constraint_name = constraint_name

    @property
    def diag(self):
        return type("Diag", (), {"constraint_name": self._constraint_name})()


@pytest.fixture(autouse=True)
def jwt_settings(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret-that-is-long-enough-for-hs256-signing")
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "480")


@pytest.fixture
def admin():
    return AdminUser(id=1, username="admin")


@pytest.fixture
def client(admin):
    """A client that is already logged in, for testing the protected routes."""
    app.dependency_overrides[require_admin] = lambda: admin
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def anon_client():
    """A client with no login cookie, for testing auth itself."""
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
def review_period():
    return {
        "id": 1,
        "name": "H1-2026",
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 6, 30),
        "status": "Open",
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
