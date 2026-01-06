from bson import ObjectId
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Annotated, Optional
from database import admin_collection, project_collection
from dependencies.auth import get_current_admin, AdminInDB
from dependencies.project_dependencies import get_project_by_id_or_404

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
    project_name: Optional[Annotated[str, Field(min_length=3, max_length=100)]]
    description: Optional[str] = None


class ProjectPublic(ProjectBase):
    admin: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



@router.get("/projects")
async def get_project():
    projects = []
    cursor = project_collection.find({})
    async for document in cursor:
        document["_id"] = str(document["_id"])
        projects.append(ProjectPublic(**document))
    return projects


@router.get("/projects/{id}")
async def get_project_by_id(id: str):
    project_doc = await get_project_by_id_or_404(id)

    if project_doc:
        return [ProjectPublic(**project_doc)]


@router.get("/{username}/projects")
async def get_user_projects(username: str):
    admin = await admin_collection.find_one({"username": username})
    if not admin:
        raise HTTPException(status_code=404, detail="User not found")

    projects = []
    cursor = project_collection.find({'admin_id': str(admin["_id"])})
    async for document in cursor:
        document["_id"] = str(document["_id"])
        projects.append(ProjectPublic(**document))
    return projects


@router.post("/projects")
async def post_project(project: ProjectBase):
    # project_id: int     # PJT_<UUID>
    # admin_id: int       # uses mongodb's _id
    # created_at: datetime
    # updated_at: datetime

    return {"message": "post_project method"}


@router.put("/projects/{id}")
async def put_project(id: int, data: ProjectBase):
    return {"message": "update_project method"}


@router.delete("/projects/{id}")
async def delete_project(id: int):
    return {"message": "delete_project method"}
