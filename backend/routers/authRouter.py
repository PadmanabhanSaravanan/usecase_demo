from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from services.authService import authenticate_user, create_access_token, signup_user
from schemas.userSchema import UserOut

router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

class SignupModel(BaseModel):
    username: str
    password: str

@router.post("/signup", response_model=UserOut)
async def signup(data: SignupModel):
    user = await signup_user(data.username, data.password)
    return user
