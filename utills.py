
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi import Depends
from router import auth
from database import SessionLocal



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(auth.get_current_user)]