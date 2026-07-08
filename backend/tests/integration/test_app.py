"""Integration test: FastAPI app boots and health endpoint responds."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "docs" in response.json()


def test_openapi_available(client: TestClient):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/auth/login" in schema["paths"]


def test_protected_route_requires_auth(client: TestClient):
    response = client.get("/api/auth/me")
    assert response.status_code in (401, 403)
