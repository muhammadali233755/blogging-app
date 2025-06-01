from fastapi import status
import pytest

def test_create_category(authorized_client):
    """Test creating a new category."""
    category_data = {
        "name": "New Category"
    }
    response = authorized_client.post("/categories/", json=category_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == category_data["name"]

def test_get_category(authorized_client, test_category):
    """Test getting a specific category."""
    response = authorized_client.get(f"/categories/{test_category['id']}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_category["id"]
    assert data["name"] == test_category["name"]

def test_get_all_categories(authorized_client, test_category):
    """Test getting all categories."""
    response = authorized_client.get("/categories/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) > 0
    assert data["total"] > 0

def test_update_category(authorized_client, test_category):
    """Test updating a category."""
    update_data = {
        "name": "Updated Category"
    }
    response = authorized_client.patch(
        f"/categories/{test_category['id']}", 
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]

def test_delete_category(authorized_client, test_category):
    """Test deleting a category."""
    response = authorized_client.delete(f"/categories/{test_category['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify category is deleted
    response = authorized_client.get(f"/categories/{test_category['id']}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_duplicate_category(authorized_client, test_category):
    """Test creating a category with duplicate name."""
    category_data = {
        "name": test_category["name"]
    }
    response = authorized_client.post("/categories/", json=category_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_category_with_posts(authorized_client, test_category, test_post):
    """Test getting category with its posts."""
    response = authorized_client.get(f"/categories/{test_category['id']}/posts")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["posts"]) > 0
    assert data["posts"][0]["id"] == test_post["id"]

