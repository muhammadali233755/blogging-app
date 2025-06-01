from fastapi import status
import pytest

@pytest.mark.auth
def test_register_user(client):
    """Test user registration."""
    response = client.post("/auth/register", json={
        "username": "newuser",
        "password": "password123"
    })
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "newuser"
    assert "password" not in data
@pytest.mark.auth
def test_register_duplicate_user(client, test_user):
    """Test duplicate user registration."""
    response = client.post("/auth/register", json={
        "username": test_user["username"],
        "password": "password123"
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
@pytest.mark.auth
def test_login_user(client, test_user):
    """Test user login."""
    response = client.post("/auth/token", data=test_user)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    response = client.post("/auth/token", data={
        "username": test_user["username"],
        "password": "wrongpass"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_refresh_token(authorized_client, test_user_token):
    """Test token refresh."""
    response = authorized_client.post("/auth/refresh")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user(authorized_client):
    """Test getting current user info."""
    response = authorized_client.get("/users/me")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"

def test_invalid_token(client):
    """Test using invalid token."""
    client.headers["Authorization"] = "Bearer invalid_token"
    response = client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_expired_token(client):
    """Test using expired token."""
    # This would require mocking the token creation time
    pass

def test_missing_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_invalid_token_format(client):
    """Test using invalid token format."""
    client.headers["Authorization"] = "Invalid format"
    response = client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

