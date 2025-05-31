from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase


BLOGCRUST_DATABASE_URL = "sqlite:///.blogsphere.db"



engine = create_engine(BLOGCRUST_DATABASE_URL,connect_args={"check_same_thread":False})



SessionLocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)



class Base(DeclarativeBase):
    pass