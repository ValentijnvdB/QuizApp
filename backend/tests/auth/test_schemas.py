"""
Tests for auth/schemas.py  (Pydantic models)
"""

import pytest
from pydantic import ValidationError


# ══════════════════════════════════════════════════════════════════════════════
# RegisterForm
# ══════════════════════════════════════════════════════════════════════════════

class TestRegisterForm:
    def test_valid_data_parses(self):
        from app.auth.schemas import RegisterForm
        form = RegisterForm(email="alice@example.com", username="alice", password="secret")
        assert form.email    == "alice@example.com"
        assert form.username == "alice"
        assert form.password == "secret"

    def test_missing_email_raises(self):
        from app.auth.schemas import RegisterForm
        with pytest.raises(ValidationError):
            RegisterForm(username="alice", password="secret")

    def test_missing_username_raises(self):
        from app.auth.schemas import RegisterForm
        with pytest.raises(ValidationError):
            RegisterForm(email="alice@example.com", password="secret")

    def test_missing_password_raises(self):
        from app.auth.schemas import RegisterForm
        with pytest.raises(ValidationError):
            RegisterForm(email="alice@example.com", username="alice")


# ══════════════════════════════════════════════════════════════════════════════
# LoginForm
# ══════════════════════════════════════════════════════════════════════════════

class TestLoginForm:
    def test_valid_data_parses(self):
        from app.auth.schemas import LoginForm
        form = LoginForm(username="alice", password="secret")
        assert form.username == "alice"
        assert form.password == "secret"

    def test_missing_username_raises(self):
        from app.auth.schemas import LoginForm
        with pytest.raises(ValidationError):
            LoginForm(password="secret")

    def test_missing_password_raises(self):
        from app.auth.schemas import LoginForm
        with pytest.raises(ValidationError):
            LoginForm(username="alice")


# ══════════════════════════════════════════════════════════════════════════════
# LogoutSchema
# ══════════════════════════════════════════════════════════════════════════════

class TestLogoutSchema:
    def test_valid_data_parses(self):
        from app.auth.schemas import LogoutSchema
        schema = LogoutSchema(refresh_token="some.jwt.token")
        assert schema.refresh_token == "some.jwt.token"

    def test_missing_refresh_token_raises(self):
        from app.auth.schemas import LogoutSchema
        with pytest.raises(ValidationError):
            LogoutSchema()


# ══════════════════════════════════════════════════════════════════════════════
# Token
# ══════════════════════════════════════════════════════════════════════════════

class TestToken:
    def test_valid_data_parses(self):
        from app.auth.schemas import Token
        token = Token(access_token="abc.def.ghi", user={"id": 1, "username": "alice"})
        assert token.access_token == "abc.def.ghi"
        assert token.token_type   == "bearer"   # default value
        assert token.user["id"]   == 1

    def test_token_type_defaults_to_bearer(self):
        from app.auth.schemas import Token
        token = Token(access_token="abc", user={})
        assert token.token_type == "bearer"

    def test_custom_token_type_is_accepted(self):
        from app.auth.schemas import Token
        token = Token(access_token="abc", token_type="mac", user={})
        assert token.token_type == "mac"

    def test_missing_access_token_raises(self):
        from app.auth.schemas import Token
        with pytest.raises(ValidationError):
            Token(user={"id": 1})

    def test_missing_user_raises(self):
        from app.auth.schemas import Token
        with pytest.raises(ValidationError):
            Token(access_token="abc")
