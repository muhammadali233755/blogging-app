import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from main import app
from utils import get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite://"  # In-memory database

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Basic fixtures
@pytest.fixture(scope="function")
def db_session():
    """Create clean database for each test."""
    Base.metadata.create_all(bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

# Authentication fixtures
@pytest.fixture(scope="function")
def test_user(client):
    """Create test user and return credentials."""
    user_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    return user_data

@pytest.fixture(scope="function")
def test_user_token(client, test_user):
    """Get authentication token for test user."""
    response = client.post("/auth/token", data=test_user)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def authorized_client(client, test_user_token):
    """Create authorized client with test user token."""
    client.headers["Authorization"] = f"Bearer {test_user_token}"
    return client

# Content fixtures
@pytest.fixture(scope="function")
def test_category(authorized_client):
    """Create test category."""
    category_data = {
        "name": "Test Category"
    }
    response = authorized_client.post("/categories/", json=category_data)
    assert response.status_code == 201
    return response.json()

@pytest.fixture(scope="function")
def test_post(authorized_client, test_category):
    """Create test post."""
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content",
        "category_id": test_category["id"]
    }
    response = authorized_client.post("/posts/", json=post_data)
    assert response.status_code == 201
    return response.json()

@pytest.fixture(scope="function")
def test_comment(authorized_client, test_post):
    """Create test comment."""
    comment_data = {
        "content": "Test comment",
        "post_id": test_post["id"]
    }
    response = authorized_client.post("/comments/", json=comment_data)
    assert response.status_code == 201
    return response.json()

@pytest.fixture(scope="function")
def test_like(authorized_client, test_post):
    """Create test like."""
    response = authorized_client.post(f"/likes/posts/{test_post['id']}")
    assert response.status_code == 201
    return response.json()
