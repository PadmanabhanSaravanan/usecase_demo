from models.todoModel import Todo
from bson import ObjectId
from db.mongo import todo_collection  # <-- import todo_collection

async def get_all_todos():
    todos = []
    async for todo in todo_collection.find():
        # todo["id"] = str(todo["_id"])
        todos.append(todo)
    return todos

async def get_todo(id: int):
    todo = await todo_collection.find_one({"id": id})
    if todo:
        # todo["id"] = str(todo["_id"])
        return todo
    return None

async def create_todo(data):
    # Find max id and increment (for compatibility)
    last = await todo_collection.find().sort("id", -1).limit(1).to_list(length=1)
    new_id = (last[0]["id"] if last else 0) + 1
    todo = {"id": new_id, "title": data.title, "completed": False}
    result = await todo_collection.insert_one(todo)
    # todo["id"] = str(result.inserted_id)
    return todo

async def update_todo(id: int, data):
    update_data = {}
    if data.title is not None:
        update_data["title"] = data.title
    if data.completed is not None:
        update_data["completed"] = data.completed
    result = await todo_collection.update_one({"id": id}, {"$set": update_data})
    if result.modified_count == 1:
        todo = await todo_collection.find_one({"id": id})
        # todo["id"] = str(todo["_id"])
        return todo
    return None

async def delete_todo(id: int):
    await todo_collection.delete_one({"id": id})