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
    assert "frac{1}{s + 1}" in response.json()["latex"]
    # Check for engineering notation u instead of Heaviside (usually in inverse)

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

def test_spectrum_endpoint():
    payload = {
        "expression": "exp(-t)*u(t)",
        "domain": "continuous"
    }
    response = client.post("/spectrum", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "magnitude" in data
    assert "phase" in data

def test_convolution_endpoint():
    payload = {
        "x_expr": "u(t)-u(t-1)",
        "h_expr": "u(t)-u(t-1)",
        "domain": "continuous"
    }
    response = client.post("/convolution", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "y" in data
    assert "frames" in data

def test_inverse_endpoint():
    payload = {
        "expression": "1/(s+1)",
        "type": "laplace"
    }
    response = client.post("/inverse", json=payload)
    assert response.status_code == 200
    data = response.json()
    # clean_output_str and .replace handle the conversion to engineering notation
    assert "e^{-t}" in data["latex"]
    assert "u[t]" in data["latex"] or "u(t)" in data["latex"]
    assert "spectrum" in data

def test_roc_surface_endpoint():
    payload = {
        "poles": [{"r": -1, "i": 0}],
        "zeros": [],
        "domain": "laplace",
        "roc_type": "causal",
        "plot_range": 5
    }
    response = client.post("/roc/surface", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "z" in data
