from fastapi import HTTPException
from database import image_collection, project_collection, admin_collection
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional

class AdminInfo(BaseModel):
    username: str
    name: str
    email: str
    photo: Optional[str] = None

class ProjectInfo(BaseModel):
    id: str
    project_name: str

async def get_image_by_id_or_404(id: str):
    try:
        image_doc = await image_collection.find_one({"_id": ObjectId(id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    if not image_doc:
        raise HTTPException(status_code=404, detail="Image not found")
    image_doc["_id"] = str(image_doc["_id"])
    return image_doc

async def get_project_info_by_id(project_id: str) -> Optional[ProjectInfo]:
    try:
        project = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not project:
            return None
        return ProjectInfo(
            id=str(project["_id"]),
            project_name=project["project_name"]
        )
    except:
        return None

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

async def get_image_with_relations(id: str):
    image_doc = await get_image_by_id_or_404(id)

    if "admin_id" in image_doc and image_doc["admin_id"]:
        admin_info = await get_admin_info_by_id(image_doc["admin_id"])
        if admin_info:
            image_doc["admin"] = admin_info

    if "project_id" in image_doc and image_doc["project_id"]:
        project_info = await get_project_info_by_id(image_doc["project_id"])
        if project_info:
            image_doc["project"] = project_info

    return image_doc
