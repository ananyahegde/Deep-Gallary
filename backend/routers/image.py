from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from database import image_collection

router = APIRouter()

class ImageMetadata(BaseModel):
    filename: str
    height: int
    width: int
    filesize: int

class Image(BaseModel):
    image_id: int
    project_id: int
    filename: str
    title: str
    embeddings: list[str]
    ai_generated_caption: str
    tags: list[str]
    metadata: ImageMetadata
    created_at: datetime
    updated_at: datetime


@router.get("/image")
async def get_image():
    return {"message": "get_image method"}

@router.get("/image/{id}")
async def get_image_by_id(id: int):
    return {"message": "get_image_by_id", "id": id}

@router.post("/image")
async def post_image(image: Image):
    return {"message": "post_image method"}

@router.put("/image/{id}")
async def put_image(id: int, data: Image):
    return {"message": "update_image method"}

@router.delete("/image/{id}")
async def delete_image(id: int):
    return {"message": "delete_image method"}
