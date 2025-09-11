from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models.userModel import User
from schemas.userSchema import UserOut
from dotenv import load_dotenv
import os
from db.mongo import user_collection  # <-- import user_collection

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def read_users():
    users = []
    async for user in user_collection.find():
        user["id"] = str(user["_id"])
        users.append(user)
    return users

async def write_users(users):
    # Not needed with MongoDB
    pass

async def get_user(username: str):
    user = await user_collection.find_one({"username": username})
    if user:
        user["id"] = str(user["_id"])
        return user
    return None

async def get_user_by_id(user_id: int):
    user = await user_collection.find_one({"id": user_id})
    if user:
        user["id"] = str(user["_id"])
        return user
    return None

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def signup_user(username: str, password: str):
    user = await get_user(username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    # Find max id and increment (for compatibility)
    last = await user_collection.find().sort("id", -1).limit(1).to_list(length=1)
    new_id = (last[0]["id"] if last else 0) + 1
    user_data = {
        "id": new_id,
        "username": username,
        "hashed_password": pwd_context.hash(password),
        "role": "user"
    }
    result = await user_collection.insert_one(user_data)
    user_data["id"] = str(result.inserted_id)
    return user_data