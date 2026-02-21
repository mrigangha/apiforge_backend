from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.databases import get_db


# override DB dependency with a mock
def override_get_db():
    db = MagicMock()
    try:
        yield db
    finally:
        pass


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)
