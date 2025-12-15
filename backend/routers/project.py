from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from database import admin_collection

router = APIRouter()

class Project(BaseModel):
    project_id: int
    admin_id: int
    project_name: str
    description: str
    created_at: datetime
    updated_at: datetime


@router.get("/project")
async def get_project():
    return {"message": "get_project method"}

@router.get("/project/{id}")
async def get_project_by_id(id: int):
    return {"message": "get_project_by_id", "id": id}

@router.post("/project")
async def post_project(project: Project):
    return {"message": "post_project method"}

@router.put("/project/{id}")
async def put_project(id: int, data: Project):
    return {"message": "update_project method"}

@router.delete("/project/{id}")
async def delete_project(id: int):
    return {"message": "delete_project method"}
