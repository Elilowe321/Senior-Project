from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from passlib.context import CryptContext
from cfb.database.database_commands import create_connection
from cfb.database.user_commands import create_user_table, insert_user
from ..pydantic_models.users import (
    get_user,
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    CreateUser,
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Database connection
def get_db():
    connection = create_connection()
    try:
        yield connection
    finally:
        connection.close()


# Function to get the current authenticated user
@router.get('/{user_id}')
def get_current_user(token: str = Depends(oauth2_scheme), connection=Depends(get_db)):
    token_data = decode_access_token(token=token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    username = token_data.get("username")
    user = get_user(username=username, connection=connection)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


# Function to register a user
@router.post("/register")
def register(
    user: CreateUser,
    connection=Depends(get_db),
):

    create_user_table(connection=connection)
    hashed_password = pwd_context.hash(user.password)

    # Create user data dictionary
    user_data = {
        "user_name": user.user_name,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "hashed_password": hashed_password,
        "paid": False,
    }
    user = insert_user(connection=connection, user_data=user_data)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not created")


# Function to give a user a token (also login)
@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), connection=Depends(get_db)
):
    
    user = get_user(username=form_data.username, connection=connection)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username Not Found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user and not verify_password(
        plain_password=form_data.password, hashed_password=user["hashed_password"], pwd_context=pwd_context
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=180)
    access_token = create_access_token(
        data={
            "user_id": user["user_id"],
            "username": user["user_name"],
            "email": user["email"],
            "paid": user["paid"],
            "earnings": user["earnings"]
        },
        expires_delta=access_token_expires,
    )

    # Return token and user
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": user["user_id"],
            "user_name": user["user_name"],
            "email": user["email"],
        },
    }

# Example of a protected route
@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["user_name"], "email": current_user["email"]}