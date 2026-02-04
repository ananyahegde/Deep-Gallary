from bson import ObjectId
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List
from database import image_collection, project_collection
from dependencies.auth import get_current_admin, AdminInDB
from dependencies.image_dependencies import (
    get_image_by_id_or_404,
    get_admin_info_by_id,
    get_project_info_by_id,
    get_image_with_relations,
    AdminInfo,
    ProjectInfo
)
from services.model_services import (
    generate_caption,
    predict_tags,
    extract_vit_embedding,
)
from PIL import Image
import os
import uuid
import numpy as np


router = APIRouter()

UPLOAD_DIR = "uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ImageMetadata(BaseModel):
    filename: str
    height: int
    width: int
    filesize: int

class ImagePublic(BaseModel):
    id: str = Field(alias="_id")
    project_id: str
    path: str
    title: Optional[str] = None
    ai_generated_caption: Optional[str] = None
    tags: List[str] = []
    embeddings: Optional[List[float]] = None
    metadata: ImageMetadata
    admin: Optional[AdminInfo] = None
    project: Optional[ProjectInfo] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class ImageUpdate(BaseModel):
    title: Optional[str] = None
    ai_generated_caption: Optional[str] = None
    tags: Optional[List[str]] = None

@router.get("/images")
async def get_images(project_id: Optional[str] = None):
    try:
        images = []
        query = {}

        if project_id:
            if not ObjectId.is_valid(project_id):
                raise HTTPException(status_code=400, detail="Invalid project ID")
            query["project_id"] = ObjectId(project_id)

        cursor = image_collection.find(query)
        async for doc in cursor:
            try:
                doc["_id"] = str(doc["_id"])
                doc["project_id"] = str(doc["project_id"])

                admin_info = await get_admin_info_by_id(doc.get("admin_id"))
                project_info = await get_project_info_by_id(doc["project_id"])

                if admin_info:
                    doc["admin"] = admin_info
                if project_info:
                    doc["project"] = project_info

                images.append(ImagePublic(**doc))
            except Exception:
                continue

        return images
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch images: {str(e)}")


@router.get("/images/search")
async def search_images(q: str):
    try:
        if not q or not q.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        query_lower = q.strip().lower()

        images = []
        cursor = image_collection.find({})

        async for doc in cursor:
            try:
                matches = False

                # Very lenient matching - just check if query word appears anywhere
                if doc.get("title") and query_lower in doc["title"].lower():
                    matches = True

                if doc.get("ai_generated_caption") and query_lower in doc["ai_generated_caption"].lower():
                    matches = True

                # Check tags
                if doc.get("tags"):
                    for tag in doc["tags"]:
                        if query_lower in tag.lower():
                            matches = True
                            break

                if matches:
                    doc["_id"] = str(doc["_id"])
                    doc["project_id"] = str(doc["project_id"])

                    admin_info = await get_admin_info_by_id(doc.get("admin_id"))
                    project_info = await get_project_info_by_id(doc["project_id"])

                    if admin_info:
                        doc["admin"] = admin_info
                    if project_info:
                        doc["project"] = project_info

                    images.append(ImagePublic(**doc))
            except Exception as e:
                print(f"Error processing image: {e}")
                continue

        return images
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/images/{id}")
async def get_image(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid image ID")

    doc = await get_image_with_relations(id)
    doc["_id"] = str(doc["_id"])
    doc["project_id"] = str(doc["project_id"])
    return ImagePublic(**doc)

@router.post("/images/ai-preview")
async def ai_preview_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    temp_path = f"/tmp/{uuid.uuid4()}"

    with open(temp_path, "wb") as f:
        f.write(contents)

    try:
        caption = generate_caption(temp_path)
        tags = predict_tags(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return {"caption": caption, "tags": tags}


@router.get("/images/{id}/similar")
async def get_similar_images(id: str, limit: int = 3):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid image ID")

    target_image = await image_collection.find_one({"_id": ObjectId(id)})
    if not target_image:
        raise HTTPException(status_code=404, detail="Image not found")

    target_tags = set(target_image.get("tags", []))

    cursor = image_collection.find({
        "admin_id": target_image["admin_id"],
        "_id": {"$ne": ObjectId(id)}
    })

    similarities = []

    async for img in cursor:
        img_tags = set(img.get("tags", []))

        if target_tags or img_tags:
            tag_sim = len(target_tags & img_tags) / max(len(target_tags | img_tags), 1)
        else:
            tag_sim = 0.0

        embedding_sim = 0.0
        if target_image.get("embeddings") and img.get("embeddings"):
            target_embedding = np.array(target_image["embeddings"], dtype=np.float32)
            img_embedding = np.array(img["embeddings"], dtype=np.float32)

            target_embedding /= np.linalg.norm(target_embedding)
            img_embedding /= np.linalg.norm(img_embedding)

            embedding_sim = float(np.dot(target_embedding, img_embedding))

        final_score = 0.7 * tag_sim + 0.3 * embedding_sim

        similarities.append((img, final_score))

    similarities.sort(key=lambda x: x[1], reverse=True)

    results = []
    for img, _ in similarities[:limit]:
        img["_id"] = str(img["_id"])
        img["project_id"] = str(img["project_id"])

        admin_info = await get_admin_info_by_id(img.get("admin_id"))
        project_info = await get_project_info_by_id(img["project_id"])

        if admin_info:
            img["admin"] = admin_info
        if project_info:
            img["project"] = project_info

        results.append(ImagePublic(**img))

    return results


@router.post("/images/{project_id}")
async def upload_image(
    project_id: str,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_admin: AdminInDB = Depends(get_current_admin)
):
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID")

    project = await project_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project["admin_id"] != str(current_admin.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    ext = file.filename.split(".")[-1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    disk_path = os.path.join(UPLOAD_DIR, filename)
    public_path = f"/uploads/images/{filename}"

    contents = await file.read()
    filesize = len(contents)

    with open(disk_path, "wb") as f:
        f.write(contents)

    img = Image.open(disk_path)
    width, height = img.size
    img.close()

    embeddings = extract_vit_embedding(disk_path)

    now = datetime.utcnow()

    image_doc = {
        "admin_id": str(current_admin.id),
        "project_id": ObjectId(project_id),
        "path": public_path,
        "title": title,
        "ai_generated_caption": caption,
        "tags": tags.split(",") if tags else [],
        "embeddings": embeddings,
        "metadata": {
            "filename": filename,
            "height": height,
            "width": width,
            "filesize": filesize
        },
        "created_at": now,
        "updated_at": now
    }

    result = await image_collection.insert_one(image_doc)

    image_doc["_id"] = str(result.inserted_id)
    image_doc["project_id"] = str(image_doc["project_id"])

    admin_info = await get_admin_info_by_id(image_doc["admin_id"])
    if admin_info:
        image_doc["admin"] = admin_info

    project_info = await get_project_info_by_id(image_doc["project_id"])
    if project_info:
        image_doc["project"] = project_info

    return ImagePublic(**image_doc)


@router.patch("/images/{id}")
async def patch_image(
    id: str,
    data: ImageUpdate,
    current_admin: AdminInDB = Depends(get_current_admin)
):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid image ID")

    image_doc = await get_image_by_id_or_404(id)

    if image_doc["admin_id"] != str(current_admin.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.utcnow()

    await image_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_data}
    )

    updated = await get_image_with_relations(id)
    updated["_id"] = str(updated["_id"])
    updated["project_id"] = str(updated["project_id"])
    return ImagePublic(**updated)

@router.delete("/images/{id}")
async def delete_image(
    id: str,
    current_admin: AdminInDB = Depends(get_current_admin)
):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid image ID")

    image_doc = await get_image_by_id_or_404(id)

    if image_doc["admin_id"] != str(current_admin.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    filename = image_doc["metadata"]["filename"]
    disk_path = os.path.join(UPLOAD_DIR, filename)

    if os.path.exists(disk_path):
        os.remove(disk_path)

    await image_collection.delete_one({"_id": ObjectId(id)})
    return {"message": "Image deleted successfully"}
