"""Login, logout, /me, and route protection."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest

import service
from models import AdminUser, LoginRequest

PASSWORD = "correct-horse-battery-staple"


@pytest.fixture(scope="module")
def password_hash():
    return service.hash_password(PASSWORD)


@pytest.fixture
def admin_row(password_hash):
    return {"id": 1, "username": "admin", "password_hash": password_hash}


def _login(client, admin_row, password=PASSWORD):
    with patch("repository.fetch_admin_by_username", return_value=admin_row):
        return client.post("/api/auth/login", json={"username": "admin", "password": password})


def test_hash_is_not_plain_password(password_hash):
    assert password_hash != PASSWORD
    assert password_hash.startswith("$argon2")


def test_login_sets_httponly_cookie(anon_client, admin_row):
    response = _login(anon_client, admin_row)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": "admin"}
    cookie = response.headers["set-cookie"].lower()
    assert "access_token=" in cookie
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "max-age=28800" in cookie


def test_login_wrong_password(anon_client, admin_row):
    response = _login(anon_client, admin_row, password="wrong")

    assert response.status_code == 401
    assert response.json()["detail"] == "INVALID_CREDENTIALS"
    assert "set-cookie" not in response.headers


def test_login_unknown_username_gives_same_error(anon_client):
    response = _login(anon_client, None)

    assert response.status_code == 401
    assert response.json()["detail"] == "INVALID_CREDENTIALS"


def test_login_requires_both_fields(anon_client):
    response = anon_client.post("/api/auth/login", json={"username": "admin"})

    assert response.status_code == 422


def test_me_without_cookie(anon_client):
    response = anon_client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "NOT_AUTHENTICATED"


def test_me_after_login(anon_client, admin_row):
    _login(anon_client, admin_row)

    response = anon_client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": "admin"}


def test_logout_clears_cookie(anon_client, admin_row):
    _login(anon_client, admin_row)

    response = anon_client.post("/api/auth/logout")

    assert response.status_code == 204
    assert 'access_token=""' in response.headers["set-cookie"]
    assert anon_client.get("/api/auth/me").status_code == 401


@pytest.mark.parametrize(
    "method, path",
    [
        ("get", "/employees"),
        ("get", "/employees/EMP101"),
        ("get", "/review-periods"),
        ("get", "/reviews"),
        ("get", "/reviews/1"),
        ("post", "/api/reviews"),
    ],
)
def test_data_routes_require_login(anon_client, method, path):
    response = getattr(anon_client, method)(path)

    assert response.status_code == 401


def test_data_route_works_after_login(anon_client, admin_row):
    _login(anon_client, admin_row)

    with patch("repository.get_all_employees", return_value=[]):
        response = anon_client.get("/employees")

    assert response.status_code == 200


def test_tampered_token_rejected(anon_client):
    token = service.create_access_token(AdminUser(id=1, username="admin"))
    anon_client.cookies.set("access_token", token[:-2] + "xx")

    assert anon_client.get("/api/auth/me").status_code == 401


def test_token_signed_with_other_secret_rejected(anon_client):
    token = jwt.encode({"sub": "1", "username": "admin", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, "other-secret-of-sufficient-length-for-hs256", algorithm="HS256")
    anon_client.cookies.set("access_token", token)

    assert anon_client.get("/api/auth/me").status_code == 401


def test_expired_token_rejected(anon_client, monkeypatch):
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "-1")
    anon_client.cookies.set("access_token", service.create_access_token(AdminUser(id=1, username="admin")))

    assert anon_client.get("/api/auth/me").status_code == 401


def test_service_login_returns_admin_and_token(admin_row):
    with patch("repository.fetch_admin_by_username", return_value=admin_row):
        admin, token = service.login(LoginRequest(username="admin", password=PASSWORD))

    assert admin == AdminUser(id=1, username="admin")
    assert service.admin_from_token(token) == admin


def test_missing_jwt_secret_raises(monkeypatch):
    monkeypatch.delenv("JWT_SECRET")

    with pytest.raises(RuntimeError):
        service.create_access_token(AdminUser(id=1, username="admin"))
