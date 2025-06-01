from fastapi import status
import pytest

def test_create_like(authorized_client, test_post):
    """Test creating a new like."""
    response = authorized_client.post(f"/likes/posts/{test_post['id']}")
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["post_id"] == test_post["id"]

def test_duplicate_like(authorized_client, test_post, test_like):
    """Test liking a post that's already liked."""
    response = authorized_client.post(f"/likes/posts/{test_post['id']}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_post_likes(authorized_client, test_post, test_like):
    """Test getting likes for a post."""
    response = authorized_client.get(f"/likes/posts/{test_post['id']}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["post_id"] == test_post["id"]
    assert data["like_count"] > 0
    assert len(data["likes"]) > 0

def test_remove_like(authorized_client, test_post, test_like):
    """Test removing a like."""
    response = authorized_client.delete(f"/likes/posts/{test_post['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify like is removed
    response = authorized_client.get(f"/likes/posts/{test_post['id']}")
    data = response.json()
    assert data["like_count"] == 0

def test_unauthorized_like_operations(client, test_post):
    """Test like operations without authentication."""
    # Try to create like
    response = client.post(f"/likes/posts/{test_post['id']}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Try to remove like
    response = client.delete(f"/likes/posts/{test_post['id']}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_user_likes(authorized_client, test_like):
    """Test getting all likes by a user."""
    response = authorized_client.get("/likes/users/me")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] > 0
    assert len(data["items"]) > 0

def test_like_nonexistent_post(authorized_client):
    """Test liking a post that doesn't exist."""
    response = authorized_client.post("/likes/posts/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

