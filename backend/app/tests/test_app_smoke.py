# app/tests/test_app_smoke.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
