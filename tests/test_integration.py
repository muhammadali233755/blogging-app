import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base
from utills import get_db

# Create test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the dependency
@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

class TestBlogIntegration:
    """
    Integration tests for the entire blog application workflow
    """
    
    def test_user_registration_and_login(self, client):
        """Test user registration and login flow"""
        # Register a new user
        registration_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        response = client.post("/register", json=registration_data)
        assert response.status_code == 201
        assert "User created successfully" in response.json()["message"]
        
        # Login with the created user
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = client.post("/login", json=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()
        
        # Save token for other tests
        token = response.json()["access_token"]
        return token
    
    def test_create_and_manage_categories(self, client):
        """Test category creation and management"""
        # First register and login to get token
        token = self.test_user_registration_and_login(client)
        
        # Create a new category
        category_data = {
            "name": "Technology",
            "description": "Tech related posts"
        }
        
        response = client.post(
            "/categories/",
            json=category_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Technology"
        
        # Get created category
        category_id = response.json()["id"]
        response = client.get(f"/categories/{category_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Technology"
        
        # Update category
        update_data = {
            "name": "Updated Technology",
            "description": "Updated description"
        }
        response = client.put(
            f"/categories/{category_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Technology"
        
        return category_id
    
    def test_post_crud_operations(self, client):
        """Test create, read, update, delete operations for posts"""
        # First register and login to get token
        token = self.test_user_registration_and_login(client)
        
        # Create a category for the post
        category_id = self.test_create_and_manage_categories(client)
        
        # Create a new post
        post_data = {
            "title": "Test Post",
            "content": "This is a test post content",
            "category_id": category_id
        }
        
        response = client.post(
            "/posts/",
            json=post_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Test Post"
        
        # Get created post
        post_id = response.json()["id"]
        response = client.get(f"/posts/{post_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Test Post"
        
        # Update post
        update_data = {
            "title": "Updated Test Post",
            "content": "This is the updated content",
            "category_id": category_id
        }
        response = client.put(
            f"/posts/{post_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Test Post"
        
        return post_id
    
    def test_comments_and_likes(self, client):
        """Test commenting and liking functionality"""
        # First register and login to get token
        token = self.test_user_registration_and_login(client)
        
        # Create a post to comment on
        post_id = self.test_post_crud_operations(client)
        
        # Add a comment to the post
        comment_data = {
            "content": "This is a test comment",
            "post_id": post_id
        }
        
        response = client.post(
            "/comments/",
            json=comment_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        assert response.json()["content"] == "This is a test comment"
        
        # Get comments for the post
        comment_id = response.json()["id"]
        response = client.get(f"/posts/{post_id}/comments")
        assert response.status_code == 200
        assert len(response.json()) > 0
        
        # Like the post
        like_data = {
            "post_id": post_id
        }
        
        response = client.post(
            "/likes/",
            json=like_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        
        # Get likes for the post
        response = client.get(f"/posts/{post_id}/likes")
        assert response.status_code == 200
        assert len(response.json()) > 0
        
        # Unlike the post
        response = client.delete(
            f"/likes/{post_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # Verify post was unliked
        response = client.get(f"/posts/{post_id}/likes")
        assert response.status_code == 200
        assert len(response.json()) == 0
    
    def test_user_permissions(self, client):
        """Test user permissions and authorization"""
        # First user registers and creates content
        token1 = self.test_user_registration_and_login(client)
        
        # Create a post with first user
        category_id = self.test_create_and_manage_categories(client)
        
        post_data = {
            "title": "First User Post",
            "content": "This post belongs to the first user",
            "category_id": category_id
        }
        
        response = client.post(
            "/posts/",
            json=post_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        post_id = response.json()["id"]
        
        # Register a second user
        registration_data = {
            "username": "seconduser",
            "email": "second@example.com",
            "password": "password456",
            "full_name": "Second User"
        }
        
        client.post("/register", json=registration_data)
        
        # Login with second user
        login_data = {
            "username": "seconduser",
            "password": "password456"
        }
        
        response = client.post("/login", json=login_data)
        token2 = response.json()["access_token"]
        
        # Second user tries to update first user's post (should fail)
        update_data = {
            "title": "Unauthorized Update",
            "content": "This should fail",
            "category_id": category_id
        }
        
        response = client.put(
            f"/posts/{post_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert response.status_code == 403
        
        # Second user tries to delete first user's post (should fail)
        response = client.delete(
            f"/posts/{post_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert response.status_code == 403
    
    def test_pagination_and_filtering(self, client):
        """Test pagination and filtering of posts"""
        # First register and login to get token
        token = self.test_user_registration_and_login(client)
        
        # Create a category
        category_id = self.test_create_and_manage_categories(client)
        
        # Create multiple posts
        for i in range(15):
            post_data = {
                "title": f"Pagination Post {i}",
                "content": f"Content for post {i}",
                "category_id": category_id
            }
            
            client.post(
                "/posts/",
                json=post_data,
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # Test pagination - first page with 10 items
        response = client.get("/posts/?skip=0&limit=10")
        assert response.status_code == 200
        assert len(response.json()) == 10
        
        # Test pagination - second page
        response = client.get("/posts/?skip=10&limit=10")
        assert response.status_code == 200
        assert len(response.json()) > 0
        
        # Test filtering by category
        response = client.get(f"/categories/{category_id}/posts")
        assert response.status_code == 200
        assert len(response.json()) > 0
    
    def test_error_handling(self, client):
        """Test error handling and validation"""
        # Try to access protected endpoint without token
        response = client.post("/posts/", json={
            "title": "Unauthorized Post",
            "content": "This should fail",
            "category_id": 1
        })
        assert response.status_code == 401
        
        # Register and login
        token = self.test_user_registration_and_login(client)
        
        # Try to create a post with invalid data (missing fields)
        response = client.post(
            "/posts/",
            json={"title": "Invalid Post"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 422  # Validation error
        
        # Try to access non-existent post
        response = client.get("/posts/9999")
        assert response.status_code == 404
    
    def test_full_blog_workflow(self, client):
        """
        Simulate a full blog workflow with multiple users interacting with posts
        """
        # Create first user
        user1_registration = {
            "username": "blogger1",
            "email": "blogger1@example.com",
            "password": "secure123",
            "full_name": "Blogger One"
        }
        client.post("/register", json=user1_registration)
        response = client.post("/login", json={
            "username": "blogger1",
            "password": "secure123"
        })
        token1 = response.json()["access_token"]
        
        # Create second user
        user2_registration = {
            "username": "blogger2",
            "email": "blogger2@example.com",
            "password": "secure456",
            "full_name": "Blogger Two"
        }
        client.post("/register", json=user2_registration)
        response = client.post("/login", json={
            "username": "blogger2",
            "password": "secure456"
        })
        token2 = response.json()["access_token"]
        
        # User 1 creates a category
        category_data = {
            "name": "Travel",
            "description": "Travel blog posts"
        }
        response = client.post(
            "/categories/",
            json=category_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        category_id = response.json()["id"]
        
        # User 1 creates a post
        post_data = {
            "title": "My Trip to Paris",
            "content": "Paris was amazing! Here's what I did...",
            "category_id": category_id
        }
        response = client.post(
            "/posts/",
            json=post_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        post_id = response.json()["id"]
        
        # User 2 comments on the post
        comment_data = {
            "content": "Great post! I love Paris too.",
            "post_id": post_id
        }
        response = client.post(
            "/comments/",
            json=comment_data,
            headers={"Authorization": f"Bearer {token2}"}
        )
        comment_id = response.json()["id"]
        
        # User 1 replies to the comment
        reply_data = {
            "content": "Thanks! Have you visited the Eiffel Tower?",
            "post_id": post_id,
            "parent_id": comment_id
        }
        client.post(
            "/comments/",
            json=reply_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        # User 2 likes the post
        client.post(
            "/likes/",
            json={"post_id": post_id},
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        # Verify the post has comments
        response = client.get(f"/posts/{post_id}/comments")
        assert response.status_code == 200
        assert len(response.json()) >= 2  # Original comment and reply
        
        # Verify the post has likes
        response = client.get(f"/posts/{post_id}/likes")
        assert response.status_code == 200
        assert len(response.json()) == 1
        
        # User 1 updates their post
        update_data = {
            "title": "My Unforgettable Trip to Paris",
            "content": "Updated with more details about my Paris trip...",
            "category_id": category_id
        }
        response = client.put(
            f"/posts/{post_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "My Unforgettable Trip to Paris"
        
        # Check post details with associated data
        response = client.get(f"/posts/{post_id}")
        assert response.status_code == 200
        post_data = response.json()
        assert post_data["title"] == "My Unforgettable Trip to Paris"
        
        # This test verifies the entire flow works correctly
        assert post_data is not None

