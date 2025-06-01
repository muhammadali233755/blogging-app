from sqlalchemy.orm import Session
from typing import Annotated, Dict, Any
from fastapi import Depends
from database import SessionLocal
from typing import Generator

def get_db() -> Generator[Session, None, None]:
    """
    Create a new database session and close it when done.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
