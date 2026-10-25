"""Tests for the database connection helper."""

from unittest.mock import patch

import pytest

import database


def test_get_connection_requires_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="DATABASE_URL is not set"):
        database.get_connection()


def test_get_connection_uses_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/test")

    with patch("database.connect") as connect:
        connection = database.get_connection()

    connect.assert_called_once_with("postgresql://user:pass@localhost:5432/test")
    assert connection is connect.return_value
