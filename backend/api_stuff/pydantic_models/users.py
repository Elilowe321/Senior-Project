from database.user_commands import get_users
from datetime import datetime, timedelta, timezone
import jwt
from jwt import PyJWTError
from pydantic import BaseModel
from typing import List, Optional


# User Model
class User:
    def __init__(
        self,
        username: str,
        first_name: str,
        last_name: str,
        email: str,
        hashed_password: str,
        paid: bool,
    ):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hashed_password = hashed_password
        self.paid = paid


# Define a Pydantic model for the request body for a user
class CreateUser(BaseModel):
    user_name: str
    first_name: str
    last_name: str
    email: str
    password: str

    class Config:
        protected_namespaces = ()


# Function to get user by username
def get_user(username: str, connection):
    users = get_users(connection=connection)

    # Check if username is in database
    for user in users:
        if user[1] == username:
            return {
                "user_id": user[0],
                "user_name": user[1],
                "first_name": user[2],
                "last_name": user[3],
                "email": user[4],
                "hashed_password": user[5],
                "paid": user[6],
                "earnings": user[7]
            }
    return None


# Function to verify password
def verify_password(plain_password, hashed_password, pwd_context):
    return pwd_context.verify(plain_password, hashed_password)


# Function to get hashed password
def get_password_hash(password, pwd_context):
    return pwd_context.hash(password)


# ========== Access Tokens ==========
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Function to create access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Function to decode access token
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            return None

        token_data = {"username": username}
        return token_data

    except PyJWTError:
        return None
