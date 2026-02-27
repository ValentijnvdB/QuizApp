"""
Tests for auth/auth.py  (get_current_user dependency)
"""

import pytest
from datetime import datetime, UTC, timedelta
from unittest.mock import MagicMock, patch

import jwt

from .conftest import SECRET_KEY, ALGORITHM, make_user, make_access_token


@patch("app.auth.utils.SECRET_KEY",      SECRET_KEY)
@patch("app.auth.auth.utils.SECRET_KEY", SECRET_KEY)
@patch("app.auth.auth.utils.ALGORITHM",  ALGORITHM)
class TestGetCurrentUser:

    @patch("app.auth.auth.db")
    def test_valid_token_returns_user(self, mock_db):
        from app.auth.auth import get_current_user
        user  = make_user()
        mock_db.get_user_by_id.return_value = user
        token  = make_access_token(user.id)
        result = get_current_user(token=token, db_session=MagicMock())
        assert result is user

    @patch("app.auth.auth.db")
    def test_invalid_token_raises_401(self, mock_db):
        from app.auth.auth import get_current_user
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            get_current_user(token="not.a.token", db_session=MagicMock())
        assert exc.value.status_code == 401

    @patch("app.auth.auth.db")
    def test_expired_token_raises_401(self, mock_db):
        from app.auth.auth import get_current_user
        from fastapi import HTTPException
        token = make_access_token(1, expired=True)
        with pytest.raises(HTTPException) as exc:
            get_current_user(token=token, db_session=MagicMock())
        assert exc.value.status_code == 401

    @patch("app.auth.auth.db")
    def test_token_for_nonexistent_user_raises_401(self, mock_db):
        from app.auth.auth import get_current_user
        from fastapi import HTTPException
        mock_db.get_user_by_id.return_value = None
        token = make_access_token(999)
        with pytest.raises(HTTPException) as exc:
            get_current_user(token=token, db_session=MagicMock())
        assert exc.value.status_code == 401

    @patch("app.auth.auth.db")
    def test_token_missing_sub_raises_401(self, mock_db):
        from app.auth.auth import get_current_user
        from fastapi import HTTPException
        # Token with no 'sub' claim
        bad_token = jwt.encode(
            {"exp": datetime.now(UTC) + timedelta(minutes=15)},
            SECRET_KEY, algorithm=ALGORITHM
        )
        with pytest.raises(HTTPException) as exc:
            get_current_user(token=bad_token, db_session=MagicMock())
        assert exc.value.status_code == 401
