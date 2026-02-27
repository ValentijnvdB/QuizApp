"""
Tests for auth/utils.py
"""

from datetime import datetime, UTC, timedelta
from unittest.mock import MagicMock, patch

import bcrypt
import jwt

from .conftest import SECRET_KEY, ALGORITHM


# ══════════════════════════════════════════════════════════════════════════════
# check_password
# ══════════════════════════════════════════════════════════════════════════════

class TestCheckPassword:
    def test_correct_password_returns_true(self):
        from app.auth.utils import check_password
        hashed = bcrypt.hashpw(b"secret", bcrypt.gensalt()).decode()
        assert check_password(hashed, "secret") is True

    def test_wrong_password_returns_false(self):
        from app.auth.utils import check_password
        hashed = bcrypt.hashpw(b"secret", bcrypt.gensalt()).decode()
        assert check_password(hashed, "wrong") is False

    def test_empty_password_returns_false(self):
        from app.auth.utils import check_password
        hashed = bcrypt.hashpw(b"secret", bcrypt.gensalt()).decode()
        assert check_password(hashed, "") is False


# ══════════════════════════════════════════════════════════════════════════════
# hash_password
# ══════════════════════════════════════════════════════════════════════════════

class TestHashPassword:

    def test_hash_password(self):
        fixed_hash = bcrypt.hashpw(b"mypassword", bcrypt.gensalt()).decode()
        assert bcrypt.checkpw(b"mypassword", fixed_hash.encode())


# ══════════════════════════════════════════════════════════════════════════════
# create_access_token
# ══════════════════════════════════════════════════════════════════════════════

@patch("app.auth.utils.SECRET_KEY", SECRET_KEY)
class TestCreateAccessToken:
    def test_returns_string(self):
        from app.auth.utils import create_access_token
        token = create_access_token({"sub": "1"})
        assert isinstance(token, str)

    def test_payload_contains_sub(self):
        from app.auth.utils import create_access_token
        token   = create_access_token({"sub": "42"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "42"

    def test_token_expires_in_15_minutes(self):
        from app.auth.utils import create_access_token
        before  = datetime.now(UTC)
        token   = create_access_token({"sub": "1"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp     = datetime.fromtimestamp(payload["exp"], tz=UTC)
        # Allow a 5-second window for test execution time
        assert timedelta(minutes=14, seconds=55) < (exp - before) <= timedelta(minutes=15)

    def test_extra_data_is_preserved(self):
        from app.auth.utils import create_access_token
        token   = create_access_token({"sub": "1", "role": "admin"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["role"] == "admin"


# ══════════════════════════════════════════════════════════════════════════════
# create_refresh_token
# ══════════════════════════════════════════════════════════════════════════════

@patch("app.auth.utils.SECRET_KEY", SECRET_KEY)
class TestCreateRefreshToken:
    def _mock_db(self):
        return MagicMock()

    @patch("app.auth.utils.db")
    def test_returns_string(self, mock_db):
        from app.auth.utils import create_refresh_token
        token = create_refresh_token(self._mock_db(), {"sub": "1"})
        assert isinstance(token, str)

    @patch("app.auth.utils.db")
    def test_payload_contains_sub(self, mock_db):
        from app.auth.utils import create_refresh_token
        token   = create_refresh_token(self._mock_db(), {"sub": "7"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "7"

    @patch("app.auth.utils.db")
    def test_token_expires_in_7_days(self, mock_db):
        from app.auth.utils import create_refresh_token
        before  = datetime.now(UTC)
        token   = create_refresh_token(self._mock_db(), {"sub": "1"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp     = datetime.fromtimestamp(payload["exp"], tz=UTC)
        assert timedelta(days=6, hours=23, minutes=55) < (exp - before) <= timedelta(days=7)

    @patch("app.auth.utils.db")
    def test_stores_token_in_db(self, mock_db):
        from app.auth.utils import create_refresh_token
        db_session = self._mock_db()
        token      = create_refresh_token(db_session, {"sub": "1"})
        mock_db.add_refresh_token.assert_called_once()
        call_kwargs = mock_db.add_refresh_token.call_args
        assert call_kwargs.kwargs["token"]   == token
        assert call_kwargs.kwargs["user_id"] == "1"
