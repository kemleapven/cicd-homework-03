import pytest
from app import app, APP_VERSION

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the homepage loads successfully and contains student details."""
    response = client.get("/")
    assert response.status_code == 200
    html_content = response.data.decode("utf-8")
    assert "Ven KemLeap" in html_content
    assert "Master - Cloud Computing" in html_content
    assert "CI/CD Release Management" in html_content
    assert APP_VERSION in html_content

def test_health_check_endpoint(client):
    """Test that the health endpoint returns UP and matching version string."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "UP"
    assert data["service"] == "cicd-web-app"
    assert data["version"] == APP_VERSION
    assert "hostname" in data
    assert "timestamp" in data

def test_api_info_endpoint(client):
    """Test that the API info endpoint returns rollback and swarm metadata."""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.get_json()
    assert data["author"] == "Ven KemLeap"
    assert data["assignment"] == "Homework 3: Release Management & Rollback"
    assert data["docker_swarm"]["rollback_support"] is True
    assert data["docker_swarm"]["replicas"] == 3
