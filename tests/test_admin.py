from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.databases import get_db
from src.services import admin_services

client = TestClient(app)

# ─── Mock Data ───────────────────────────────────────────


def make_mock_user(id, name, email, role):
    user = MagicMock()
    user.id = id
    user.name = name
    user.email = email
    user.role = role
    return user


mock_admin = make_mock_user(99, "Admin", "admin@example.com", "admin")

mock_users = [
    make_mock_user(1, "Alice", "alice@example.com", "user"),
    make_mock_user(2, "Bob", "bob@example.com", "user"),
    make_mock_user(3, "Carol", "carol@example.com", "user"),
]

# ─── GET /admin/users ─────────────────────────────────────


def test_get_users_as_admin():
    app.dependency_overrides[admin_services.getCurrentAdmin] = lambda: (
        "admin@example.com"
    )
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch(
        "src.services.admin_services.get_user_for_admin", return_value=mock_users
    ):
        res = client.get("/api/v1/admin/users")

        assert res.status_code == 200
        assert res.json()["message"] == "Get users"
        assert len(res.json()["users"]) == 3

    app.dependency_overrides.clear()


def test_get_users_unauthenticated():
    from fastapi import HTTPException

    def raise_401():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[admin_services.getCurrentAdmin] = raise_401

    res = client.get("/api/v1/admin/users")
    assert res.status_code == 401
    assert res.json()["detail"] == "Not authenticated"

    app.dependency_overrides.clear()


def test_get_users_as_regular_user_forbidden():
    from fastapi import HTTPException

    def raise_403():
        raise HTTPException(status_code=403, detail="Admins only")

    app.dependency_overrides[admin_services.getCurrentAdmin] = raise_403

    res = client.get("/api/v1/admin/users")
    assert res.status_code == 403
    assert res.json()["detail"] == "Admins only"

    app.dependency_overrides.clear()


def test_get_users_returns_empty_list():
    app.dependency_overrides[admin_services.getCurrentAdmin] = lambda: (
        "admin@example.com"
    )
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch("src.services.admin_services.get_user_for_admin", return_value=[]):
        res = client.get("/api/v1/admin/users")

        assert res.status_code == 200
        assert res.json()["users"] == []

    app.dependency_overrides.clear()


# ─── PATCH /admin/users/{user_id}/promote ────────────────


def test_promote_user_success():
    # use SimpleNamespace or plain object instead of MagicMock
    from types import SimpleNamespace

    promoted_user = SimpleNamespace(
        id=1, name="Alice", email="alice@example.com", role="admin"
    )

    app.dependency_overrides[admin_services.getCurrentAdmin] = lambda: (
        "admin@example.com"
    )
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch("src.services.admin_services.user_promote", return_value=promoted_user):
        res = client.patch("/api/v1/admin/users/1/promote")

        assert res.status_code == 200
        assert res.json()["message"] == "alice@example.com promoted to admin"
        assert res.json()["user"]["role"] == "admin"

    app.dependency_overrides.clear()


def test_promote_user_not_found():
    from fastapi import HTTPException

    app.dependency_overrides[admin_services.getCurrentAdmin] = lambda: (
        "admin@example.com"
    )
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch("src.services.admin_services.user_promote") as mock_promote:
        mock_promote.side_effect = HTTPException(
            status_code=404, detail="User not found"
        )

        res = client.patch("/api/v1/admin/users/999/promote")

        assert res.status_code == 404
        assert res.json()["detail"] == "User not found"

    app.dependency_overrides.clear()


def test_promote_already_admin():
    from fastapi import HTTPException

    app.dependency_overrides[admin_services.getCurrentAdmin] = lambda: (
        "admin@example.com"
    )
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch("src.services.admin_services.user_promote") as mock_promote:
        mock_promote.side_effect = HTTPException(
            status_code=400, detail="User is already an admin"
        )

        res = client.patch("/api/v1/admin/users/2/promote")

        assert res.status_code == 400
        assert "already" in res.json()["detail"].lower()

    app.dependency_overrides.clear()


def test_promote_unauthenticated():
    from fastapi import HTTPException

    def raise_401():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[admin_services.getCurrentAdmin] = raise_401

    res = client.patch("/api/v1/admin/users/1/promote")
    assert res.status_code == 401

    app.dependency_overrides.clear()


def test_promote_as_regular_user_forbidden():
    from fastapi import HTTPException

    def raise_403():
        raise HTTPException(status_code=403, detail="Admins only")

    app.dependency_overrides[admin_services.getCurrentAdmin] = raise_403

    res = client.patch("/api/v1/admin/users/1/promote")
    assert res.status_code == 403

    app.dependency_overrides.clear()


# ─── DELETE /admin/users/{user_id} ───────────────────────


def test_delete_user_success():
    app.dependency_overrides[admin_services.getCurrentAdmin] = lambda: (
        "admin@example.com"
    )
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch("src.services.admin_services.delete_user", return_value=None):
        res = client.delete("/api/v1/admin/users/1")

        assert res.status_code == 200
        assert res.json()["message"] == "User deleted successfully"

    app.dependency_overrides.clear()


def test_delete_user_not_found():
    from fastapi import HTTPException

    app.dependency_overrides[admin_services.getCurrentAdmin] = lambda: (
        "admin@example.com"
    )
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch("src.services.admin_services.delete_user") as mock_delete:
        mock_delete.side_effect = HTTPException(
            status_code=404, detail="User not found"
        )

        res = client.delete("/api/v1/admin/users/999")

        assert res.status_code == 404
        assert res.json()["detail"] == "User not found"

    app.dependency_overrides.clear()


def test_delete_user_unauthenticated():
    from fastapi import HTTPException

    def raise_401():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[admin_services.getCurrentAdmin] = raise_401

    res = client.delete("/api/v1/admin/users/1")
    assert res.status_code == 401

    app.dependency_overrides.clear()


def test_delete_user_as_regular_user_forbidden():
    from fastapi import HTTPException

    def raise_403():
        raise HTTPException(status_code=403, detail="Admins only")

    app.dependency_overrides[admin_services.getCurrentAdmin] = raise_403

    res = client.delete("/api/v1/admin/users/1")
    assert res.status_code == 403

    app.dependency_overrides.clear()
