import sys
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests._artifacts import requires_trained_model
import pytest


def _unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@medialert.test"


class TestRegistration:

    def test_register_returns_201_and_no_password(self, client):
        email = _unique_email()
        response = client.post("/register", json={"email": email, "password": "validpassword123"})
        assert response.status_code == 201
        body = response.json()
        assert body["email"] == email
        assert "password" not in body
        assert "hashed_password" not in body

    def test_register_duplicate_email_returns_409(self, client):
        email = _unique_email()
        client.post("/register", json={"email": email, "password": "validpassword123"})
        response = client.post("/register", json={"email": email, "password": "differentpassword456"})
        assert response.status_code == 409

    def test_register_short_password_rejected(self, client):
        email = _unique_email()
        response = client.post("/register", json={"email": email, "password": "short"})
        assert response.status_code == 422


class TestLogin:

    def test_login_with_correct_password_succeeds(self, client):
        email = _unique_email()
        client.post("/register", json={"email": email, "password": "correctpassword123"})
        response = client.post("/login", data={"username": email, "password": "correctpassword123"})
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_login_with_wrong_password_returns_401(self, client):
        email = _unique_email()
        client.post("/register", json={"email": email, "password": "correctpassword123"})
        response = client.post("/login", data={"username": email, "password": "wrongpassword"})
        assert response.status_code == 401

    def test_login_with_nonexistent_email_returns_401(self, client):
        response = client.post("/login", data={"username": "nobody@nowhere.test", "password": "whatever123"})
        assert response.status_code == 401

    def test_password_hash_is_not_plaintext(self, client):
        """Guards against the most basic possible auth failure: storing
        passwords in plain text."""
        from backend.db import SessionLocal
        from backend.db_models import User

        email = _unique_email()
        password = "definitelynotstoredasplaintext"
        client.post("/register", json={"email": email, "password": password})

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            assert user.hashed_password != password
            assert password not in user.hashed_password
            assert user.hashed_password.startswith("$2b$")  # bcrypt hash prefix
        finally:
            db.close()


@requires_trained_model
class TestRouteProtection:
    """Uses a fresh, unauthenticated TestClient - deliberately NOT the
    shared `client` fixture, since that one is pre-authenticated by design
    and would defeat the purpose of these specific tests."""

    def test_predict_without_token_returns_401(self, valid_payload):
        from fastapi.testclient import TestClient
        from backend.main import app
        with TestClient(app) as anon_client:
            response = anon_client.post("/predict", json=valid_payload)
            assert response.status_code == 401

    def test_history_without_token_returns_401(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        with TestClient(app) as anon_client:
            response = anon_client.get("/history/ANY-REFERENCE")
            assert response.status_code == 401

    def test_dashboard_without_token_returns_401(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        with TestClient(app) as anon_client:
            response = anon_client.get("/dashboard")
            assert response.status_code == 401

    def test_predict_with_garbage_token_returns_401(self, valid_payload):
        from fastapi.testclient import TestClient
        from backend.main import app
        with TestClient(app) as anon_client:
            response = anon_client.post(
                "/predict", json=valid_payload,
                headers={"Authorization": "Bearer not.a.real.token"},
            )
            assert response.status_code == 401

    def test_form_options_does_not_require_auth(self):
        """Deliberate design choice: the frontend needs this before a user
        has logged in, to render the form at all."""
        from fastapi.testclient import TestClient
        from backend.main import app
        with TestClient(app) as anon_client:
            response = anon_client.get("/form-options")
            assert response.status_code == 200

    def test_health_does_not_require_auth(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        with TestClient(app) as anon_client:
            response = anon_client.get("/health")
            assert response.status_code == 200

    def test_me_without_token_returns_401(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        with TestClient(app) as anon_client:
            response = anon_client.get("/me")
            assert response.status_code == 401


class TestProfileEndpoint:

    def test_me_returns_own_email_and_no_password(self, client):
        response = client.get("/me")
        assert response.status_code == 200
        body = response.json()
        assert "email" in body
        assert "created_at" in body
        assert "password" not in body
        assert "hashed_password" not in body

    def test_created_at_includes_explicit_timezone_marker(self, client):
        """Guards against a real bug found during development: SQLite
        returns naive UTC timestamps with no timezone marker, which
        JavaScript's Date parser then silently treats as the browser's
        local time - making every displayed timestamp wrong by the
        viewer's UTC offset (5h30m for Sri Lanka). The API response must
        always include an explicit offset (Z or +00:00), never a bare
        "2026-08-17T21:10:26" with nothing after the seconds."""
        response = client.get("/me")
        created_at = response.json()["created_at"]
        assert created_at.endswith("Z") or "+" in created_at[-6:], (
            f"created_at '{created_at}' has no explicit timezone marker - "
            "this will be parsed incorrectly by JavaScript clients."
        )