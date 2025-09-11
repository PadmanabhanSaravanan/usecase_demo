from fastapi import FastAPI
from monitor import monitor
from routers import todoRouter
from routers import authRouter  # add this import
from routers import userRouter
from routers import healthRouter
from routers.featureFlagRouter import router as feature_flag_router
from error.todoNotFound import todo_not_found_exception_handler, TodoNotFoundException
from error.userNotFound import user_not_found_exception_handler, UserNotFoundException
from passlib.context import CryptContext
from db.mongo import user_collection
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Todo App", version="1.0.0", description="Todo application API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def init_admin_user():
    admin = await user_collection.find_one({"username": "admin"})
    if not admin:
        admin_user = {
            "id": 1,
            "username": "admin",
            "hashed_password": pwd_context.hash("admin"),
            "role": "admin"
        }
        await user_collection.insert_one(admin_user)

@app.on_event("startup")
async def startup_event():
    await init_admin_user()

app.include_router(authRouter.router, prefix="/auth", tags=["auth"])
app.include_router(userRouter.router, prefix="/users", tags=["users"])
app.include_router(todoRouter.router, prefix="/todos", tags=["todos"])
app.include_router(healthRouter.router, prefix="/health", tags=["health"])
app.include_router(monitor.router, prefix="/metrics", tags=["metrics"])
app.include_router(feature_flag_router)

app.add_exception_handler(TodoNotFoundException, todo_not_found_exception_handler)
app.add_exception_handler(UserNotFoundException, user_not_found_exception_handler)