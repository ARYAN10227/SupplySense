"""API integration tests: health check and the register → login → protected-route flow."""

import pytest
from fastapi.testclient import TestClient

from main import app

USER = {
    "shop_name": "Test Medical Store",
    "business_type": "pharmacy",
    "city": "Nagpur",
    "state": "Maharashtra",
    "phone": "9000000001",
    "password": "secret123",
}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_register_login_and_protected_route(client):
    r = client.post("/api/auth/register", json=USER)
    assert r.status_code == 201, r.text
    assert r.json()["user"]["shop_name"] == USER["shop_name"]

    r = client.post("/api/auth/login", json={"phone": USER["phone"], "password": USER["password"]})
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = client.get("/api/inventory", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text


def test_duplicate_phone_is_rejected(client):
    r = client.post("/api/auth/register", json=USER)
    assert r.status_code == 409


def test_wrong_password_is_rejected(client):
    r = client.post("/api/auth/login", json={"phone": USER["phone"], "password": "wrongpass"})
    assert r.status_code == 401


def test_protected_route_requires_token(client):
    r = client.get("/api/inventory")
    assert r.status_code in (401, 403)


def test_invalid_business_type_fails_validation(client):
    r = client.post("/api/auth/register", json={**USER, "phone": "9000000002", "business_type": "casino"})
    assert r.status_code == 422
