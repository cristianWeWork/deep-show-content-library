
from datetime import datetime, timedelta
from typing import Annotated
import os
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from pydantic import BaseModel
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import pymssql
from .models import users

SERVER = os.getenv('SERVER')
DATABASE = os.getenv('DATABASE')
USERNAME = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

TODAY = datetime.now()

engine = sqlalchemy.create_engine(
    f'mssql+pymssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}')
Session = sessionmaker(bind=engine)
session = Session()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# class UserInDB(User):
#     hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def getUsers():
    usersList = session.query(users).all()
    
    return usersList

def getUser(userName):
    try:
        stmt = session.query(users).where(users.username == userName)
        if stmt is not None:
            for user in session.scalars(stmt):
                return user
        else:
            raise 'No se encuentra ese usuario, mi niño'
    except exc.NoResultFound as e:
        error = str(e.__dict__['orig'])
        return error
    

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def register_new_user(username, password, email, name, surname):
    hashed_pass = get_password_hash(password)
    new_user = users(username=username, password = hashed_pass, email = email, name = name, surname = surname, created_at=TODAY, subscription=1 )
    session.add(new_user)
    session.commit()

    return {"message": "Usuario registrado correctamente"}

def get_user_login( username: str, ):
    stmt = session.query(users).where(users.username == username )
    
    for user in session.scalars(stmt):
        return user
        

def authenticate_user(username: str, password: str):
    user = get_user_login(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    try:
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except:
        session_clear()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=15)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt
        except:
            session_clear()
            
            
def session_clear(exception=None):
    session.rollback()
    if exception and Session.is_active:
        Session.rollback()

