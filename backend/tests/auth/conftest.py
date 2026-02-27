"""
Shared fixtures and helpers used across all auth test modules.
pytest automatically loads this file — no imports needed in test files.
"""

from datetime import datetime, UTC, timedelta
from unittest.mock import MagicMock, patch

import bcrypt
import jwt
import pytest
from fastapi import FastAPI


SECRET_KEY = "test-secret-key"
ALGORITHM  = "HS256"


# ── factory helpers ────────────────────────────────────────────────────────────

def make_user(id=1, username="alice", email="alice@example.com",
              password="password123"):
    user = MagicMock()
    user.id       = id
    user.username = username
    user.email    = email
    user.hashed_password = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt()
    ).decode()
    return user


def make_access_token(user_id: int, expired=False) -> str:
    delta = timedelta(minutes=-1) if expired else timedelta(minutes=15)
    exp   = datetime.now(UTC) + delta
    return jwt.encode({"sub": str(user_id), "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)


def make_refresh_token(user_id: int, expired=False) -> str:
    delta = timedelta(days=-1) if expired else timedelta(days=7)
    exp   = datetime.now(UTC) + delta
    return jwt.encode({"sub": str(user_id), "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)


# ── fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def test_app():
    """
    Build a minimal FastAPI app with the auth router, overriding the db
    dependency so no real database is needed.
    Returns (app, fake_db).
    """
    from app.auth.router import router
    from app import db as database

    app = FastAPI()
    fake_db = MagicMock()

    app.dependency_overrides[database.get_db] = lambda: fake_db

    patcher = patch("app.auth.router.database", fake_db)
    patcher.start()
    app.include_router(router, prefix="/auth")

    yield app, fake_db

    patcher.stop()
