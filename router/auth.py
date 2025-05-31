from fastapi import Depends,APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from starlette import status
from jose import JWTError, jwt
from model import User
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
from datetime import datetime,timedelta,timezone

from schemas.user import UserCreate, UserResponse


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)



SECRET_KEY = "d2fe8y238ewncne3rykqwclyqqurry2o"
ALGORITHM = "HS256"



bcrypt_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    
db_dependency = Annotated[Session,Depends(get_db)]

class CreateUserRequest(BaseModel):
    username:str
    password :str
    role_id : int = 2


class TokenModel(BaseModel):
    access_token:str
    token_type:str


@router.post("/register", status_code=201, response_model=UserResponse)
def register_user( user_data: UserCreate, db: db_dependency):
    
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = bcrypt_context.hash(user_data.password)
    
    
    user = User(username=user_data.username,password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user 





@router.post("/token", response_model=TokenModel)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=30)
    token = create_access_token(user.username, user.id, access_token_expires)

    return {"access_token": token, "token_type": "bearer"}
    
    
    
    

def authenticate_user(username:str,password:str,db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user



def create_access_token(username:str,user_id:int,expires_delta:timedelta):
    encode = {"sub":username,"id":user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)




def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str = payload.get("sub")
        user_id:int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail = "Could not validate user")
        return {"username":username,"id":user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate user")



