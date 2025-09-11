from fastapi import APIRouter, Depends
from schemas.todoSchema import TodoOut, TodoCreate, TodoUpdate
from services import todoService as todo_service
from error.todoNotFound import TodoNotFoundException
from services.authService import get_current_user, get_current_admin

router = APIRouter()

@router.get("/", response_model=list[TodoOut])
async def list_todos(current_user: dict = Depends(get_current_user)):
    return await todo_service.get_all_todos()

@router.get("/{id}", response_model=TodoOut)
async def get_todo(id: int, current_user: dict = Depends(get_current_user)):
    todo = await todo_service.get_todo(id)
    if not todo:
        raise TodoNotFoundException(id)
    return todo

@router.post("/", response_model=TodoOut, status_code=201)
async def create_todo(data: TodoCreate, current_user: dict = Depends(get_current_admin)):
    return await todo_service.create_todo(data)

@router.put("/{id}", response_model=TodoOut)
async def update_todo(id: int, data: TodoUpdate, current_user: dict = Depends(get_current_admin)):
    todo = await todo_service.update_todo(id, data)
    if not todo:
        raise TodoNotFoundException(id)
    return todo

@router.delete("/{id}", status_code=204)
async def delete_todo(id: int, current_user: dict = Depends(get_current_admin)):
    todo = await todo_service.get_todo(id)
    if not todo:
        raise TodoNotFoundException(id)
    await todo_service.delete_todo(id)