from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from database import admin_collection
from bson import json_util
import json

router = APIRouter()

class Admin(BaseModel):
    admin_id: int
    username: str
    name: str
    email: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    photo: Optional[str] = None     # bytes if we are storing the image itself
    description: Optional[str] = None
    contact: str


@router.get("/admin")
async def get_admin():
    admins = []
    cursor = admin_collection.find({})
    async for document in cursor:
        admins.append(Admin(**document))
    return admins


@router.get("/admin/{id}")
async def get_admin_by_id(id: int):
    admin = await admin_collection.find_one({"admin_id": id})
    admin = json.loads(json_util.dumps(admin))
    return admin


@router.post("/admin")
async def post_admin(admin: Admin):
    document = admin.model_dump()
    result = await admin_collection.insert_one(document)
    document["_id"] = str(result.inserted_id)

    return {"message": "Admin created successfully", "admin": document}


@router.put("/admin/{id}")
async def put_admin(id: int, data: Admin):
    result = await admin_collection.update_one(
        {"admin_id": id},
        {"$set": data.model_dump()}
    )

    if result.matched_count == 0:
            return {"error": "Admin not found"}

    document = await admin_collection.find_one({"admin_id": id})
    if document:
        document["_id"] = str(document["_id"])

    return {"message": "Admin updated successfully", "data": document}


@router.delete("/admin/{id}")
async def delete_admin(id: int):
    await admin_collection.delete_one({"admin_id": id})
    return {"message": "Admin deleted successfully"}
