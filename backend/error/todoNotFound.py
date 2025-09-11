from fastapi import Request, status
from fastapi.responses import JSONResponse

class TodoNotFoundException(Exception):
    def __init__(self, todo_id: int):
        self.todo_id = todo_id

def todo_not_found_exception_handler(request: Request, exc: TodoNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": f"Todo with id {exc.todo_id} not found."}
    )
