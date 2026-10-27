"""Business rules — sits between the API layer and the repository."""

import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
from psycopg.errors import ForeignKeyViolation, UniqueViolation
from pwdlib import PasswordHash

import repository
from models import AdminUser, LoginRequest, ReviewCreate

JWT_ALGORITHM = "HS256"

password_hasher = PasswordHash.recommended()  # argon2
# Verified when the username doesn't exist, so a wrong username takes as long as a wrong password.
_DUMMY_HASH = password_hasher.hash("dummy-password-for-timing")


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def _jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET is not set")
    return secret


def token_lifetime_minutes() -> int:
    return int(os.getenv("JWT_EXPIRE_MINUTES", "480"))


def create_access_token(admin: AdminUser) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(admin.id),
        "username": admin.username,
        "iat": now,
        "exp": now + timedelta(minutes=token_lifetime_minutes()),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=JWT_ALGORITHM)


def admin_from_token(token: str) -> AdminUser | None:
    """Return the admin a token was issued to, or None if it is invalid, tampered with or expired."""
    try:
        payload = jwt.decode(
            token,
            _jwt_secret(),
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
        return AdminUser(id=int(payload["sub"]), username=payload["username"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None


def login(credentials: LoginRequest) -> tuple[AdminUser, str]:
    # Business rule: wrong username and wrong password give the same error, so usernames can't be probed.
    invalid = HTTPException(status_code=401, detail="INVALID_CREDENTIALS")
    row = repository.fetch_admin_by_username(credentials.username)
    if row is None:
        password_hasher.verify(credentials.password, _DUMMY_HASH)
        raise invalid
    if not password_hasher.verify(credentials.password, row["password_hash"]):
        raise invalid
    admin = AdminUser(id=row["id"], username=row["username"])
    return admin, create_access_token(admin)


def list_employees() -> list[dict]:
    return repository.get_all_employees()


def list_review_periods() -> list[dict]:
    return repository.get_all_review_periods()


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