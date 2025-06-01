import pytest
from alembic.config import Config
from alembic import command
from pathlib import Path

from database import Base, engine
from config import get_settings

settings = get_settings()

def test_create_initial_tables():
    """Test creating all tables from models."""
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Verify all tables exist
    inspector = engine.dialect.inspector(engine)
    tables = inspector.get_table_names()
    
    expected_tables = [
        "users",
        "categories",
        "posts",
        "comments",
        "likes",
        "views"
    ]
    
    for table in expected_tables:
        assert table in tables

@pytest.mark.slow
def test_migrations_head():
    """Test running migrations to head."""
    # Get project root directory
    root_dir = Path(__file__).parent.parent
    
    # Configure Alembic
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(root_dir / "migrations"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    
    try:
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        assert True
    except Exception as e:
        assert False, f"Migration failed: {str(e)}"

@pytest.mark.slow
def test_migrations_downgrade():
    """Test downgrading migrations."""
    # Get project root directory
    root_dir = Path(__file__).parent.parent
    
    # Configure Alembic
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(root_dir / "migrations"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    
    try:
        # Downgrade all migrations
        command.downgrade(alembic_cfg, "base")
        
        # Verify all tables are dropped
        inspector = engine.dialect.inspector(engine)
        tables = inspector.get_table_names()
        assert len(tables) == 0
        
        # Upgrade again to restore state
        command.upgrade(alembic_cfg, "head")
        assert True
    except Exception as e:
        assert False, f"Migration failed: {str(e)}"

def test_table_relationships():
    """Test database relationships and constraints."""
    inspector = engine.dialect.inspector(engine)
    
    # Test foreign keys in posts table
    fks = inspector.get_foreign_keys("posts")
    fk_columns = [fk["constrained_columns"][0] for fk in fks]
    assert "user_id" in fk_columns
    assert "category_id" in fk_columns
    
    # Test foreign keys in comments table
    fks = inspector.get_foreign_keys("comments")
    fk_columns = [fk["constrained_columns"][0] for fk in fks]
    assert "user_id" in fk_columns
    assert "post_id" in fk_columns
    
    # Test foreign keys in likes table
    fks = inspector.get_foreign_keys("likes")
    fk_columns = [fk["constrained_columns"][0] for fk in fks]
    assert "user_id" in fk_columns
    assert "post_id" in fk_columns

def test_table_indices():
    """Test database indices."""
    inspector = engine.dialect.inspector(engine)
    
    # Test post indices
    indices = inspector.get_indexes("posts")
    index_names = [idx["name"] for idx in indices]
    assert "ix_posts_user_id" in index_names
    assert "ix_posts_category_id" in index_names
    
    # Test comment indices
    indices = inspector.get_indexes("comments")
    index_names = [idx["name"] for idx in indices]
    assert "ix_comments_user_id" in index_names
    assert "ix_comments_post_id" in index_names
    
    # Test like indices
    indices = inspector.get_indexes("likes")
    index_names = [idx["name"] for idx in indices]
    assert "ix_likes_user_id" in index_names
    assert "ix_likes_post_id" in index_names

