from fastapi import status
import pytest

def test_create_comment(authorized_client, test_post):
    """Test creating a new comment."""
    comment_data = {
        "content": "New comment",
        "post_id": test_post["id"]
    }
    response = authorized_client.post("/comments/", json=comment_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["content"] == comment_data["content"]
    assert data["post_id"] == test_post["id"]

def test_get_post_comments(authorized_client, test_post, test_comment):
    """Test getting comments for a post."""
    response = authorized_client.get(f"/comments/posts/{test_post['id']}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] > 0
    assert len(data["items"]) > 0
    assert data["items"][0]["content"] == test_comment["content"]

def test_update_comment(authorized_client, test_comment):
    """Test updating a comment."""
    update_data = {
        "content": "Updated comment"
    }
    response = authorized_client.patch(
        f"/comments/{test_comment['id']}", 
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["content"] == update_data["content"]

def test_delete_comment(authorized_client, test_comment):
    """Test deleting a comment."""
    response = authorized_client.delete(f"/comments/{test_comment['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify comment is deleted
    response = authorized_client.get(f"/comments/{test_comment['id']}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_unauthorized_comment_operations(client, test_post, test_comment):
    """Test comment operations without authentication."""
    # Try to create comment
    response = client.post("/comments/", json={
        "content": "Unauthorized comment",
        "post_id": test_post["id"]
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Try to update comment
    response = client.patch(f"/comments/{test_comment['id']}", json={
        "content": "Unauthorized update"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Try to delete comment
    response = client.delete(f"/comments/{test_comment['id']}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_other_user_comment(authorized_client, test_comment):
    """Test updating another user's comment."""
    # Create another user and their comment
    other_user_data = {
        "username": "otheruser",
        "password": "password123"
    }
    response = authorized_client.post("/auth/register", json=other_user_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    response = authorized_client.post("/auth/token", data=other_user_data)
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]
    
    # Try to update other user's comment
    authorized_client.headers["Authorization"] = f"Bearer {token}"
    response = authorized_client.patch(
        f"/comments/{test_comment['id']}", 
        json={"content": "Should fail"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

