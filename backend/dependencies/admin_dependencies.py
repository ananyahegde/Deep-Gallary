from fastapi import HTTPException, UploadFile
from database import admin_collection
from typing import Optional
import os
import uuid
from pathlib import Path

ADMIN_PROFILE_DIR = "uploads/profiles"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


async def get_admin_by_field_or_404(username: Optional[str] = None, email: Optional[str] = None):
    filter_query = {}
    if username:
        filter_query["username"] = username
    if email:
        filter_query["email"] = email
    if not filter_query:
        return None
    admin_doc = await admin_collection.find_one(filter_query)
    if not admin_doc:
        raise HTTPException(status_code=404, detail="Admin not found")
    admin_doc["_id"] = str(admin_doc["_id"])
    return admin_doc


async def verify_unique_username(username: str):
    if await admin_collection.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="Username is already taken")


async def verify_unique_email(email: str):
    if await admin_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email is already taken")


def validate_admin_profile_image(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    extension = file.filename.split(".")[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )


async def save_admin_profile_image(file: UploadFile) -> str:
    validate_admin_profile_image(file)

    Path(ADMIN_PROFILE_DIR).mkdir(parents=True, exist_ok=True)

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    extension = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{extension}"
    file_path = os.path.join(ADMIN_PROFILE_DIR, unique_filename)

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB")

    with open(file_path, "wb") as f:
        f.write(contents)

    return file_path


def delete_admin_profile_image(file_path: str):
    """Delete admin profile image from disk"""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass
