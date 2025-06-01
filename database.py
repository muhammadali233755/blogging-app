from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import Engine
from typing import Generator

from config import get_settings

settings = get_settings()

# Use database URL from settings
engine: Engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

class Base(DeclarativeBase):
    pass
