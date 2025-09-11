from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://4.213.222.83:27017/fastapi_db")
client = AsyncIOMotorClient(MONGO_URL)
database = client.fastapi_db

user_collection = database.get_collection("users")
todo_collection = database.get_collection("todos")
