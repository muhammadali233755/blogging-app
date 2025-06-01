from fastapi import status
import pytest

@pytest.mark.db
def test_create_post(authorized_client, test_category):
    """Test creating a new post."""
    post_data = {
        "title": "New Post",
        "content": "This is a new post content",
        "category_id": test_category["id"]
    }
    response = authorized_client.post("/posts/", json=post_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == post_data["title"]
    assert data["content"] == post_data["content"]
    assert data["category_id"] == test_category["id"]

@pytest.mark.api
def test_get_post(authorized_client, test_post):
    """Test getting a specific post."""
    response = authorized_client.get(f"/posts/{test_post['id']}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_post["id"]
    assert data["title"] == test_post["title"]

def test_get_all_posts(authorized_client, test_post):
    """Test getting all posts."""
    response = authorized_client.get("/posts/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) > 0
    assert data["total"] > 0

def test_update_post(authorized_client, test_post):
    """Test updating a post."""
    update_data = {
        "title": "Updated Post",
        "content": "Updated content"
    }
    response = authorized_client.patch(
        f"/posts/{test_post['id']}", 
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["content"] == update_data["content"]

def test_delete_post(authorized_client, test_post):
    """Test deleting a post."""
    response = authorized_client.delete(f"/posts/{test_post['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify post is deleted
    response = authorized_client.get(f"/posts/{test_post['id']}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_unauthorized_post_operations(client, test_post):
    """Test post operations without authentication."""
    # Try to create post
    response = client.post("/posts/", json={
        "title": "Unauthorized Post",
        "content": "This should fail",
        "category_id": 1
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Try to update post
    response = client.patch(f"/posts/{test_post['id']}", json={
        "title": "Unauthorized Update"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Try to delete post
    response = client.delete(f"/posts/{test_post['id']}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

