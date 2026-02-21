from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

# ─── Mock Data ───────────────────────────────────────────

mock_user = MagicMock()
mock_user.email = "alice@example.com"
mock_user.role = "user"

# ─── /register ───────────────────────────────────────────


def test_register_success():
    with patch("src.services.auth_service.create_user") as mock_create:
        mock_create.return_value = mock_user

        res = client.post(
            "/api/v1/auth/register",
            json={
                "name": "Alice",
                "email": "alice@example.com",
                "password": "secret123",
            },
        )

        assert res.status_code == 200
        assert res.json()["message"] == "User registered successfully"
        assert res.json()["email"] == "alice@example.com"


def test_register_duplicate_email():
    with patch("src.services.auth_service.create_user") as mock_create:
        from fastapi import HTTPException

        mock_create.side_effect = HTTPException(
            status_code=400, detail="Email already registered"
        )

        res = client.post(
            "/api/v1/auth/register",
            json={
                "name": "Alice",
                "email": "alice@example.com",
                "password": "secret123",
            },
        )

        assert res.status_code == 400
        assert res.json()["detail"] == "Email already registered"


def test_register_missing_fields():
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com"
            # missing name and password
        },
    )
    assert res.status_code == 422  # validation error


# ─── /login ──────────────────────────────────────────────


def test_login_success():
    with (
        patch("src.services.auth_service.verify_user", return_value=mock_user),
        patch(
            "src.services.auth_service.create_accesstoken",
            return_value="mock_access_token",
        ),
        patch(
            "src.services.auth_service.create_refreshtoken",
            return_value="mock_refresh_token",
        ),
    ):
        res = client.post(
            "/api/v1/auth/login",
            json={"email": "alice@example.com", "password": "secret123"},
        )

        assert res.status_code == 200
        assert res.json()["access_token"] == "mock_access_token"
        assert res.json()["token_type"] == "bearer"

        # refresh token should be in httponly cookie
        assert "refresh_token" in res.cookies


def test_login_wrong_password():
    with patch("src.services.auth_service.verify_user") as mock_verify:
        from fastapi import HTTPException

        mock_verify.side_effect = HTTPException(
            status_code=401, detail="Invalid credentials"
        )

        res = client.post(
            "/api/v1/auth/login",
            json={"email": "alice@example.com", "password": "wrongpassword"},
        )

        assert res.status_code == 401
        assert res.json()["detail"] == "Invalid credentials"


def test_login_nonexistent_user():
    with patch("src.services.auth_service.verify_user") as mock_verify:
        from fastapi import HTTPException

        mock_verify.side_effect = HTTPException(
            status_code=404, detail="User not found"
        )

        res = client.post(
            "/api/v1/auth/login",
            json={"email": "ghost@example.com", "password": "secret123"},
        )

        assert res.status_code == 404


# ─── /refresh ────────────────────────────────────────────


def test_refresh_success():
    from src.services.auth_service import get_user_from_refresh_token

    # override the dependency instead of patching
    app.dependency_overrides[get_user_from_refresh_token] = lambda: "alice@example.com"

    with patch(
        "src.services.auth_service.create_accesstoken", return_value="new_access_token"
    ):
        client.cookies.set("refresh_token", "valid_refresh_token")
        res = client.post("/api/v1/auth/refresh")

        assert res.status_code == 200
        assert res.json()["access_token"] == "new_access_token"

    app.dependency_overrides.clear()  # clean up after test


def test_refresh_no_cookie():
    with patch("src.services.auth_service.get_user_from_refresh_token") as mock_get:
        from fastapi import HTTPException

        mock_get.side_effect = HTTPException(status_code=401, detail="No refresh token")

        # clear cookies
        client.cookies.clear()

        res = client.post("/api/v1/auth/refresh")

        assert res.status_code == 401


def test_refresh_expired_token():
    from fastapi import HTTPException

    from src.services.auth_service import get_user_from_refresh_token

    def raise_expired():
        raise HTTPException(status_code=401, detail="Refresh token expired")

    app.dependency_overrides[get_user_from_refresh_token] = raise_expired

    client.cookies.set("refresh_token", "expired_token")
    res = client.post("/api/v1/auth/refresh")

    assert res.status_code == 401
    assert "expired" in res.json()["detail"].lower()

    app.dependency_overrides.clear()
