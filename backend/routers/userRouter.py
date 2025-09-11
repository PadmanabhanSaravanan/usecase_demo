from fastapi import APIRouter, Depends
from services.authService import read_users, get_user_by_id, get_current_admin
from error.userNotFound import UserNotFoundException
from schemas.userSchema import UserOut

router = APIRouter()

@router.get("/", response_model=list[UserOut])
async def list_users(current_user: dict = Depends(get_current_admin)):
    return await read_users()

@router.get("/{id}", response_model=UserOut)
async def get_user(id: int, current_user: dict = Depends(get_current_admin)):
    user = await get_user_by_id(id)
    if not user:
        raise UserNotFoundException(id)
    return user
