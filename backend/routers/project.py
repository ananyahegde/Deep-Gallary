from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Annotated, Optional
import os
from database import admin_collection, project_collection
from dependencies.auth import get_current_admin, AdminInDB
from dependencies.project_dependencies import get_project_by_id_or_404, get_admin_info_by_id, get_project_with_admin, AdminInfo

load_dotenv()

router = APIRouter()

class ProjectBase(BaseModel):
    project_name: Annotated[str, Field(min_length=3, max_length=100)]
    description: Optional[str] = None

    @field_validator("project_name")
    @classmethod
    def validate_projectname(cls, v: str):
        if len(v.strip()) == 0:
            raise ValueError("Project Name cannot be empty")
        return v

class ProjectUpdate(BaseModel):
    project_name: Optional[Annotated[str, Field(min_length=3, max_length=100)]] = None
    description: Optional[str] = None

class ProjectPublic(ProjectBase):
    id: str = Field(alias="_id")
    admin: Optional[AdminInfo] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

@router.get("/projects")
async def get_project():
    try:
        projects = []
        cursor = project_collection.find({})
        async for document in cursor:
            try:
                document["_id"] = str(document["_id"])
                admin_info = await get_admin_info_by_id(document["admin_id"])
                if admin_info:
                    document["admin"] = admin_info
                projects.append(ProjectPublic(**document))
            except Exception:
                continue
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")

@router.get("/projects/{id}")
async def get_project_by_id(id: str):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid project ID format")

        project_doc = await get_project_with_admin(id)
        return ProjectPublic(**project_doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch project: {str(e)}")

@router.get("/{username}/projects")
async def get_user_projects(username: str):
    try:
        if not username or len(username.strip()) == 0:
            raise HTTPException(status_code=400, detail="Username cannot be empty")

        admin = await admin_collection.find_one({"username": username})
        if not admin:
            raise HTTPException(status_code=404, detail="User not found")

        admin_info = AdminInfo(
            username=admin["username"],
            name=admin["name"],
            email=admin["email"],
            photo=admin.get("photo")
        )

        projects = []
        cursor = project_collection.find({'admin_id': str(admin["_id"])})
        async for document in cursor:
            try:
                document["_id"] = str(document["_id"])
                document["admin"] = admin_info
                projects.append(ProjectPublic(**document))
            except Exception:
                continue

        return projects
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user projects: {str(e)}")

@router.post("/projects")
async def post_project(
    project: ProjectBase,
    current_admin: AdminInDB = Depends(get_current_admin)
):
    try:
        now = datetime.utcnow()
        project_doc = {
            "admin_id": str(current_admin.id),
            "project_name": project.project_name,
            "description": project.description,
            "created_at": now,
            "updated_at": now
        }

        result = await project_collection.insert_one(project_doc)

        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create project")

        project_doc["_id"] = str(result.inserted_id)

        admin_info = await get_admin_info_by_id(str(current_admin.id))
        if not admin_info:
            raise HTTPException(status_code=404, detail="Admin not found")

        project_doc["admin"] = admin_info

        return ProjectPublic(**project_doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@router.patch("/projects/{id}")
async def patch_project(
    id: str,
    data: ProjectUpdate,
    current_admin: AdminInDB = Depends(get_current_admin)
):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid project ID format")

        project_doc = await get_project_by_id_or_404(id)

        if project_doc["admin_id"] != str(current_admin.id):
            raise HTTPException(status_code=403, detail="Not authorized to update this project")

        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        update_data["updated_at"] = datetime.utcnow()

        result = await project_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")

        updated_project = await get_project_with_admin(id)

        return ProjectPublic(**updated_project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")

@router.delete("/projects/{id}")
async def delete_project(
    id: str,
    current_admin: AdminInDB = Depends(get_current_admin)
):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid project ID format")

        project_doc = await get_project_by_id_or_404(id)

        if project_doc["admin_id"] != str(current_admin.id):
            raise HTTPException(status_code=403, detail="Not authorized to delete this project")

        result = await project_collection.delete_one({"_id": ObjectId(id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")

        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")
