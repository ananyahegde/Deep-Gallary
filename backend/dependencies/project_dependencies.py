from fastapi import HTTPException
from database import project_collection, admin_collection
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional

class AdminInfo(BaseModel):
    username: str
    name: str
    email: str
    photo: Optional[str] = None

async def get_project_by_id_or_404(id: str):
    try:
        project_doc = await project_collection.find_one({"_id": ObjectId(id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    if not project_doc:
        raise HTTPException(status_code=404, detail="Project not found")
    project_doc["_id"] = str(project_doc["_id"])
    return project_doc

async def get_admin_info_by_id(admin_id: str) -> Optional[AdminInfo]:
    try:
        admin = await admin_collection.find_one({"_id": ObjectId(admin_id)})
        if not admin:
            return None
        return AdminInfo(
            username=admin["username"],
            name=admin["name"],
            email=admin["email"],
            photo=admin.get("photo")
        )
    except:
        return None

async def get_project_with_admin(id: str):
    project_doc = await get_project_by_id_or_404(id)
    admin_info = await get_admin_info_by_id(project_doc["admin_id"])
    if admin_info:
        project_doc["admin"] = admin_info
    return project_doc
