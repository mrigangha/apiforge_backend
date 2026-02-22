# tests/test_posts.py
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.databases import get_db
from src.services import auth_service

client = TestClient(app)

# ─── Mock Data ───────────────────────────────────────────


def make_mock_post(id, title, content, owner_email):
    return SimpleNamespace(id=id, title=title, content=content, owner_email=owner_email)


mock_post = make_mock_post(1, "Test Title", "Test Content", "alice@example.com")

mock_posts = [
    make_mock_post(1, "Post One", "Content One", "alice@example.com"),
    make_mock_post(2, "Post Two", "Content Two", "alice@example.com"),
    make_mock_post(3, "Post Three", "Content Three", "alice@example.com"),
]

# ─── POST /posts ─────────────────────────────────────────


def test_create_post_success():
    app.dependency_overrides[auth_service.getCurrentUser] = lambda: "alice@example.com"
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch(
        "src.services.post_services.create_post_for_user", return_value=mock_post
    ):
        res = client.post(
            "/api/v1/posts", json={"title": "Test Title", "content": "Test Content"}
        )

        assert res.status_code == 200
        assert res.json()["message"] == "Post created successfully"
        assert res.json()["post"]["title"] == "Test Title"

    app.dependency_overrides.clear()


def test_create_post_unauthenticated():
    from fastapi import HTTPException

    def raise_401():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[auth_service.getCurrentUser] = raise_401

    res = client.post(
        "/api/v1/posts", json={"title": "Test Title", "content": "Test Content"}
    )

    assert res.status_code == 401

    app.dependency_overrides.clear()


def test_create_post_missing_fields():
    app.dependency_overrides[auth_service.getCurrentUser] = lambda: "alice@example.com"

    res = client.post(
        "/api/v1/posts",
        json={
            "title": "Only Title"
            # missing content
        },
    )

    assert res.status_code == 422

    app.dependency_overrides.clear()


# ─── GET /posts ──────────────────────────────────────────


def test_get_all_posts_success():
    app.dependency_overrides[auth_service.getCurrentUser] = lambda: "alice@example.com"
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch("src.services.post_services.get_all_posts", return_value=mock_posts):
        res = client.get("/api/v1/posts")

        assert res.status_code == 200
        assert res.json()["message"] == "Posts retrieved successfully"
        assert len(res.json()["posts"]) == 3

    app.dependency_overrides.clear()


def test_get_all_posts_empty():
    app.dependency_overrides[auth_service.getCurrentUser] = lambda: "alice@example.com"
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch("src.services.post_services.get_all_posts", return_value=[]):
        res = client.get("/api/v1/posts")

        assert res.status_code == 200
        assert res.json()["posts"] == []

    app.dependency_overrides.clear()


def test_get_all_posts_unauthenticated():
    from fastapi import HTTPException

    def raise_401():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[auth_service.getCurrentUser] = raise_401

    res = client.get("/api/v1/posts")
    assert res.status_code == 401

    app.dependency_overrides.clear()


# ─── GET /posts/{post_id} ────────────────────────────────


def test_get_post_success():
    app.dependency_overrides[auth_service.getCurrentUser] = lambda: "alice@example.com"
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch("src.services.post_services.get_post", return_value=mock_post):
        res = client.get("/api/v1/posts/1")

        assert res.status_code == 200
        assert res.json()["message"] == "Post retrieved successfully"
        assert res.json()["post"]["id"] == 1

    app.dependency_overrides.clear()


def test_get_post_not_found():
    app.dependency_overrides[auth_service.getCurrentUser] = lambda: "alice@example.com"
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch("src.services.post_services.get_post", return_value=None):
        res = client.get("/api/v1/posts/999")

        assert res.status_code == 404
        assert res.json()["detail"] == "Post not found"

    app.dependency_overrides.clear()


def test_get_post_unauthenticated():
    from fastapi import HTTPException

    def raise_401():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[auth_service.getCurrentUser] = raise_401

    res = client.get("/api/v1/posts/1")
    assert res.status_code == 401

    app.dependency_overrides.clear()


# ─── PUT /posts/{post_id} ────────────────────────────────


def test_update_post_success():
    updated_post = make_mock_post(
        1, "Updated Title", "Updated Content", "alice@example.com"
    )

    app.dependency_overrides[auth_service.getCurrentUser] = lambda: "alice@example.com"
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch("src.services.post_services.update_post", return_value=updated_post):
        res = client.put(
            "/api/v1/posts/1",
            json={"title": "Updated Title", "content": "Updated Content"},
        )

        assert res.status_code == 200
        assert res.json()["message"] == "Post updated successfully"
        assert res.json()["post"]["title"] == "Updated Title"

    app.dependency_overrides.clear()


def test_update_post_not_found():
    app.dependency_overrides[auth_service.getCurrentUser] = lambda: "alice@example.com"
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch("src.services.post_services.update_post", return_value=None):
        res = client.put(
            "/api/v1/posts/999",
            json={"title": "Updated Title", "content": "Updated Content"},
        )

        assert res.status_code == 404
        assert res.json()["detail"] == "Post not found"

    app.dependency_overrides.clear()


def test_update_post_unauthenticated():
    from fastapi import HTTPException

    def raise_401():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[auth_service.getCurrentUser] = raise_401

    res = client.put(
        "/api/v1/posts/1", json={"title": "Updated Title", "content": "Updated Content"}
    )

    assert res.status_code == 401

    app.dependency_overrides.clear()


def test_update_post_missing_fields():
    app.dependency_overrides[auth_service.getCurrentUser] = lambda: "alice@example.com"

    res = client.put(
        "/api/v1/posts/1",
        json={
            "title": "Only Title"
            # missing content
        },
    )

    assert res.status_code == 422

    app.dependency_overrides.clear()


# ─── DELETE /posts/{post_id} ─────────────────────────────


def test_delete_post_success():
    app.dependency_overrides[auth_service.getCurrentUser] = lambda: "alice@example.com"
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch("src.services.post_services.delete_post", return_value=mock_post):
        res = client.delete("/api/v1/posts/1")

        assert res.status_code == 200
        assert res.json()["message"] == "Post deleted successfully"

    app.dependency_overrides.clear()


def test_delete_post_not_found():
    app.dependency_overrides[auth_service.getCurrentUser] = lambda: "alice@example.com"
    app.dependency_overrides[get_db] = lambda: MagicMock()

    with patch("src.services.post_services.delete_post", return_value=None):
        res = client.delete("/api/v1/posts/999")

        assert res.status_code == 404
        assert res.json()["detail"] == "Post not found"

    app.dependency_overrides.clear()


def test_delete_post_unauthenticated():
    from fastapi import HTTPException

    def raise_401():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[auth_service.getCurrentUser] = raise_401

    res = client.delete("/api/v1/posts/1")
    assert res.status_code == 401

    app.dependency_overrides.clear()
