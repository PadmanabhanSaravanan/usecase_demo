from fastapi import Request, status
from fastapi.responses import JSONResponse

class UserNotFoundException(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id

def user_not_found_exception_handler(request: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": f"User with id {exc.user_id} not found."}
    )
