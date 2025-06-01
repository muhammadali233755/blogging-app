from fastapi import status
import pytest
import time
from config import get_settings

@pytest.mark.api
def test_rate_limiting(client):
    """Test rate limiting middleware."""
    settings = get_settings()
    
    # Make requests up to the limit
    for _ in range(settings.RATE_LIMIT):
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
    
    # Next request should be rate limited
    response = client.get("/health")
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    
    # Wait 60 seconds and try again (only in non-development)
    if settings.ENVIRONMENT != "development":
        time.sleep(60)
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

def test_security_headers(client):
    """Test security headers middleware."""
    response = client.get("/health")
    headers = response.headers
    
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-XSS-Protection"] == "1; mode=block"
    assert "Strict-Transport-Security" in headers
    assert "Referrer-Policy" in headers
    assert headers["Cache-Control"] == "no-store"

def test_request_id(client):
    """Test request ID middleware."""
    response = client.get("/health")
    assert "X-Request-ID" in response.headers
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) > 0

def test_cors_headers(client):
    """Test CORS middleware."""
    settings = get_settings()
    
    response = client.get(
        "/health",
        headers={"Origin": settings.ALLOWED_ORIGINS[0]}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "Access-Control-Allow-Origin" in response.headers

def test_gzip_compression(client):
    """Test gzip compression middleware."""
    response = client.get(
        "/health",
        headers={"Accept-Encoding": "gzip"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.headers.get("Content-Encoding") == "gzip"

@pytest.mark.api
def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data
    assert "security_warnings" in data

def test_api_info(client):
    """Test API info endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "description" in data
    assert "endpoints" in data
    assert "auth_required" in data

@pytest.mark.parametrize("path", [
    "/nonexistent",
    "/api/v1/unknown",
    "/posts/99999999"
])
def test_404_handling(client, path):
    """Test 404 error handling."""
    response = client.get(path)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data

@pytest.mark.parametrize("method,path", [
    ("POST", "/posts/"),
    ("PATCH", "/posts/1"),
    ("DELETE", "/posts/1"),
    ("POST", "/comments/"),
    ("POST", "/likes/posts/1")
])
def test_401_handling(client, method, path):
    """Test 401 error handling for protected endpoints."""
    response = client.request(method, path)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
    assert "WWW-Authenticate" in response.headers

def test_validation_error_handling(client):
    """Test validation error handling."""
    response = client.post("/auth/register", json={
        "username": "u",  # Too short
        "password": "p"   # Too short
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data

@pytest.mark.db
def test_database_connection(db_session):
    """Test database connection."""
    try:
        db_session.execute("SELECT 1")
        assert True
    except Exception:
        assert False, "Database connection failed"

