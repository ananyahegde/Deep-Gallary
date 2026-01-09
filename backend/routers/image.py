from bson import ObjectId
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Annotated, Optional
from database import image_collection, project_collection, admin_collection
from dependencies.auth import get_current_admin, AdminInDB
from dependencies.project_dependencies import AdminInfo, get_admin_info_by_id

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

class ProjectInfo(BaseModel):
    id: str
    project_name: str

class ImagePublic(ImageBase):
    id: str = Field(alias="_id")
    admin: Optional[AdminInfo] = None
    project: Optional[ProjectInfo] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

@router.get("/images")
async def get_image():
    try:
        images = []
        cursor = image_collection.find({})
        async for document in cursor:
            try:
                document["_id"] = str(document["_id"])

                admin_info = await get_admin_info_by_id(document["admin_id"])
                if admin_info:
                    document["admin"] = admin_info

                project = await project_collection.find_one({"_id": ObjectId(document["project_id"])})
                if project:
                    document["project"] = ProjectInfo(
                        id=str(project["_id"]),
                        project_name=project["project_name"]
                    )

                images.append(ImagePublic(**document))
            except Exception:
                continue
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch images: {str(e)}")

@router.get("/images/{id}")
async def get_image_by_id(id: str):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid image ID format")

        image_doc = await image_collection.find_one({"_id": ObjectId(id)})
        if not image_doc:
            raise HTTPException(status_code=404, detail="Image not found")

        image_doc["_id"] = str(image_doc["_id"])

        admin_info = await get_admin_info_by_id(image_doc["admin_id"])
        if admin_info:
            image_doc["admin"] = admin_info

        project = await project_collection.find_one({"_id": ObjectId(image_doc["project_id"])})
        if project:
            image_doc["project"] = ProjectInfo(
                id=str(project["_id"]),
                project_name=project["project_name"]
            )

        return ImagePublic(**image_doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(e)}")

@router.post("/images/{project_id}")
async def post_image(
    project_id: str,
    image: ImageBase,
    current_admin: AdminInDB = Depends(get_current_admin)
):
    try:
        if not ObjectId.is_valid(project_id):
            raise HTTPException(status_code=400, detail="Invalid project ID format")

        project = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        if project["admin_id"] != str(current_admin.id):
            raise HTTPException(status_code=403, detail="Not authorized to add images to this project")

        now = datetime.utcnow()
        image_doc = {
            "admin_id": str(current_admin.id),
            "project_id": project_id,
            "title": image.title,
            "embeddings": image.embeddings,
            "caption": image.caption,
            "tags": image.tags,
            "metadata": image.metadata.model_dump(),
            "created_at": now,
            "updated_at": now
        }

        result = await image_collection.insert_one(image_doc)

        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create image")

        image_doc["_id"] = str(result.inserted_id)

        admin_info = await get_admin_info_by_id(str(current_admin.id))
        if admin_info:
            image_doc["admin"] = admin_info

        image_doc["project"] = ProjectInfo(
            id=str(project["_id"]),
            project_name=project["project_name"]
        )

        return ImagePublic(**image_doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create image: {str(e)}")

@router.patch("/images/{id}")
async def patch_image(
    id: str,
    data: ImageUpdate,
    current_admin: AdminInDB = Depends(get_current_admin)
):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid image ID format")

        image_doc = await image_collection.find_one({"_id": ObjectId(id)})
        if not image_doc:
            raise HTTPException(status_code=404, detail="Image not found")

        if image_doc["admin_id"] != str(current_admin.id):
            raise HTTPException(status_code=403, detail="Not authorized to update this image")

        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        update_data["updated_at"] = datetime.utcnow()

        result = await image_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Image not found")

        updated_image = await image_collection.find_one({"_id": ObjectId(id)})
        updated_image["_id"] = str(updated_image["_id"])

        admin_info = await get_admin_info_by_id(str(current_admin.id))
        if admin_info:
            updated_image["admin"] = admin_info

        project = await project_collection.find_one({"_id": ObjectId(updated_image["project_id"])})
        if project:
            updated_image["project"] = ProjectInfo(
                id=str(project["_id"]),
                project_name=project["project_name"]
            )

        return ImagePublic(**updated_image)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update image: {str(e)}")

@router.delete("/images/{id}")
async def delete_image(
    id: str,
    current_admin: AdminInDB = Depends(get_current_admin)
):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid image ID format")

        image_doc = await image_collection.find_one({"_id": ObjectId(id)})
        if not image_doc:
            raise HTTPException(status_code=404, detail="Image not found")

        if image_doc["admin_id"] != str(current_admin.id):
            raise HTTPException(status_code=403, detail="Not authorized to delete this image")

        result = await image_collection.delete_one({"_id": ObjectId(id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Image not found")

        return {"message": "Image deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")
