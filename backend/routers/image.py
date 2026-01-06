from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from database import image_collection
from typing import Annotated, Optional

router = APIRouter()

class ImageMetadata(BaseModel):
    filename: Annotated[str, Field(min_length=1, max_length=255)]
    height: Annotated[int, Field(gt=0, le=50000)]
    width: Annotated[int, Field(gt=0, le=50000)]
    filesize: Annotated[int, Field(gt=0)]


class ImageBase(BaseModel):
    title: Optional[Annotated[str, Field(max_length=200)]] = None
    embeddings: list[float] = []
    caption: Optional[Annotated[str, Field(max_length=1000)]] = None
    tags: Optional[Annotated[list[str], Field(max_length=10)]] = None
    metadata: ImageMetadata


class ImageUpdate(BaseModel):
    title: Optional[str] = None
    caption: Optional[str] = None
    tags: Optional[list[str]] = None


class ImagePublic(ImageBase):
    admin: Optional[str] = None
    project: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



@router.get("/images")
async def get_image():
    return {"message": "get_image method"}

@router.get("/images/{id}")
async def get_image_by_id(id: int):
    return {"message": "get_image_by_id", "id": id}

@router.post("/images")
async def post_image(image: ImageBase):
    # image_id: int
    # project_id: int
    # created_at: Optional[datetime] = None
    # updated_at: Optional[datetime] = None

    return {"message": "post_image method"}

@router.put("/images/{id}")
async def put_image(id: int, data: ImageBase):
    return {"message": "update_image method"}

@router.delete("/images/{id}")
async def delete_image(id: int):
    return {"message": "delete_image method"}
