"""
Tests for auth/router.py  (FastAPI routes via TestClient)
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from .conftest import SECRET_KEY, ALGORITHM, make_user, make_refresh_token


# ══════════════════════════════════════════════════════════════════════════════
# POST /auth/register
# ══════════════════════════════════════════════════════════════════════════════

@patch("app.auth.utils.SECRET_KEY",        SECRET_KEY)
@patch("app.auth.router.utils.SECRET_KEY", SECRET_KEY)
@patch("app.auth.router.utils.ALGORITHM",  ALGORITHM)
class TestRegisterRoute:

    def test_register_success(self, test_app):
        app, fake_db = test_app
        fake_db.create_user.return_value = None
        client   = TestClient(app)
        response = client.post("/auth/register", json={
            "email": "bob@example.com",
            "username": "bob",
            "password": "hunter2"
        })
        assert response.status_code == 200
        fake_db.create_user.assert_called_once()

    def test_register_stores_hashed_password(self, test_app):
        """The password stored in the DB must not be the plain-text password."""
        app, fake_db = test_app
        client = TestClient(app)
        client.post("/auth/register", json={
            "email": "bob@example.com",
            "username": "bob",
            "password": "hunter2"
        })
        _, kwargs = fake_db.create_user.call_args
        assert kwargs["hashed_password"] != "hunter2"
        assert kwargs["hashed_password"].startswith("$2b$")


# ══════════════════════════════════════════════════════════════════════════════
# POST /auth/login
# ══════════════════════════════════════════════════════════════════════════════

@patch("app.auth.utils.SECRET_KEY",        SECRET_KEY)
@patch("app.auth.router.utils.SECRET_KEY", SECRET_KEY)
@patch("app.auth.router.utils.ALGORITHM",  ALGORITHM)
class TestLoginRoute:

    def test_login_success_returns_access_token(self, test_app):
        app, fake_db = test_app
        user = make_user()
        fake_db.get_user_by_username.return_value = user
        fake_db.add_refresh_token.return_value    = None
        client   = TestClient(app, raise_server_exceptions=True)
        response = client.post("/auth/login", json={
            "username": "alice", "password": "password123"
        })
        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert body["user"]["username"] == "alice"

    def test_login_sets_httponly_refresh_token_cookie(self, test_app):
        app, fake_db = test_app
        user = make_user()
        fake_db.get_user_by_username.return_value = user
        fake_db.add_refresh_token.return_value    = None
        client   = TestClient(app)
        response = client.post("/auth/login", json={
            "username": "alice", "password": "password123"
        })
        assert "refresh_token" in response.cookies

    def test_login_wrong_password_returns_400(self, test_app):
        app, fake_db = test_app
        user = make_user()
        fake_db.get_user_by_username.return_value = user
        client   = TestClient(app)
        response = client.post("/auth/login", json={
            "username": "alice", "password": "wrongpassword"
        })
        assert response.status_code == 400

    def test_login_unknown_user_returns_400(self, test_app):
        app, fake_db = test_app
        fake_db.get_user_by_username.return_value = None
        client   = TestClient(app)
        response = client.post("/auth/login", json={
            "username": "ghost", "password": "password123"
        })
        assert response.status_code == 400


# ══════════════════════════════════════════════════════════════════════════════
# POST /auth/refresh
# ══════════════════════════════════════════════════════════════════════════════

@patch("app.auth.utils.SECRET_KEY",        SECRET_KEY)
@patch("app.auth.router.utils.SECRET_KEY", SECRET_KEY)
@patch("app.auth.router.utils.ALGORITHM",  ALGORITHM)
class TestRefreshRoute:

    def test_valid_refresh_token_returns_new_access_token(self, test_app):
        app, fake_db = test_app
        user  = make_user()
        token = make_refresh_token(user.id)
        fake_db.get_refresh_token_by_token.return_value = MagicMock()  # token exists
        fake_db.get_user_by_id.return_value             = user
        client = TestClient(app)
        client.cookies.set("refresh_token", token)
        response = client.post("/auth/refresh")
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_missing_cookie_returns_401(self, test_app):
        app, _ = test_app
        client   = TestClient(app)
        response = client.post("/auth/refresh")
        assert response.status_code == 401

    def test_expired_refresh_token_returns_401(self, test_app):
        app, fake_db = test_app
        token = make_refresh_token(1, expired=True)
        client = TestClient(app)
        client.cookies.set("refresh_token", token)
        response = client.post("/auth/refresh")
        assert response.status_code == 401

    def test_revoked_refresh_token_returns_401(self, test_app):
        """Token is valid JWT but not present in the DB (already revoked)."""
        app, fake_db = test_app
        token = make_refresh_token(1)
        fake_db.get_refresh_token_by_token.return_value = None  # not in DB
        client = TestClient(app)
        client.cookies.set("refresh_token", token)
        response = client.post("/auth/refresh")
        assert response.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# POST /auth/logout
# ══════════════════════════════════════════════════════════════════════════════

@patch("app.auth.utils.SECRET_KEY",        SECRET_KEY)
@patch("app.auth.router.utils.SECRET_KEY", SECRET_KEY)
class TestLogoutRoute:

    def test_logout_success(self, test_app):
        app, fake_db = test_app
        fake_db.revoke_refresh_token.return_value = None
        token  = make_refresh_token(1)
        client = TestClient(app)
        client.cookies.set("refresh_token", token)
        response = client.post("/auth/logout")
        assert response.status_code == 200
        assert response.json() == {"message": "You have been logged out"}

    def test_logout_calls_revoke_with_token(self, test_app):
        app, fake_db = test_app
        fake_db.revoke_refresh_token.return_value = None
        token  = make_refresh_token(1)
        client = TestClient(app)
        client.cookies.set("refresh_token", token)
        client.post("/auth/logout")
        fake_db.revoke_refresh_token.assert_called_once_with(
            fake_db,  # any db session
            token=token
        )

    def test_logout_clears_cookie(self, test_app):
        app, fake_db = test_app
        fake_db.revoke_refresh_token.return_value = None
        token  = make_refresh_token(1)
        client = TestClient(app)
        client.cookies.set("refresh_token", token)
        response = client.post("/auth/logout")
        # Cookie should be deleted (absent or empty) after logout
        assert not response.cookies.get("refresh_token")

    def test_logout_missing_cookie_returns_401(self, test_app):
        app, _ = test_app
        client   = TestClient(app)
        response = client.post("/auth/logout")
        assert response.status_code == 401