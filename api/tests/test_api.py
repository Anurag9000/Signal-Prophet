import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_plot_endpoint():
    payload = {
        "expression": "sin(t)",
        "t_min": -5,
        "t_max": 5,
        "domain": "continuous"
    }
    response = client.post("/plot", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "x" in data
    assert "y" in data
    assert len(data["x"]) > 0

def test_transform_endpoint():
    payload = {
        "expression": "exp(-t)*u(t)",
        "type": "laplace"
    }
    response = client.post("/transform", json=payload)
    assert response.status_code == 200
    assert "1/(s + 1)" in response.json()["latex"]

def test_analyze_system_endpoint():
    payload = {
        "equation": "x(t)",
        "domain": "continuous"
    }
    response = client.post("/analyze_system", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "properties" in data
    assert data["properties"]["linearity"]["status"] == "yes"

def test_detect_period_endpoint():
    payload = {
        "expression": "sin(t)",
        "domain": "continuous"
    }
    response = client.post("/fourier/detect-period", json=payload)
    assert response.status_code == 200
    assert response.json()["period"] is not None
    assert "Detected period" in response.json()["message"]

def test_parse_transfer_function():
    payload = {
        "expression": "1/(s+1)",
        "variable": "s"
    }
    response = client.post("/parse_transfer_function", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["poles"]) == 1
    assert data["poles"][0]["r"] == -1
