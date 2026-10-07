import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_sketch_endpoint():
    response = client.post("/api/v1/generate/sketch", data={"prompt": "Cyberpunk Samurai"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_steps"] == 5
    assert len(data["steps"]) == 5

def test_paint_endpoint():
    response = client.post("/api/v1/generate/paint", data={"prompt": "Impressionist Sunrise"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_steps"] == 5

def test_pixel_endpoint():
    response = client.post("/api/v1/generate/pixel", data={"prompt": "Retro Knight Sprite"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_steps"] == 5
