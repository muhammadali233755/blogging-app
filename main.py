from fastapi import FastAPI,Depends, HTTPException
from database import engine,SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
import model
from router import category
import router.auth as auth
from starlette import status
from utills import user_dependency,db_dependency


app = FastAPI(
    title="Blogging Site",
    version="1.0.0"
)
app.include_router(auth.router)
app.include_router(category.router)


model.Base.metadata.create_all(bind=engine)  



# def populate_roles(db: Session):
#     default_roles = ["admin", "user"]
#     for role_name in default_roles:
#         role = db.query(model.Role).filter(model.Role.name == role_name).first()
#         if not role:
#             db.add(model.Role(name=role_name))
#     db.commit()



# with engine.connect() as conn:
#     db = SessionLocal()
#     populate_roles(db)
#     db.close()



        
    




@app.get("/",status_code=status.HTTP_200_OK)
def user(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail = "Authentication Failed")
    return {"User":user}
