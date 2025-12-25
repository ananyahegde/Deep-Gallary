from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from pymongo.errors import DuplicateKeyError
from typing import Optional, Annotated
import re
from database import admin_collection
from dependencies.auth import get_password_hash

router = APIRouter()

class AdminBase(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=30)]
    name: Annotated[str, Field(min_length=2, max_length=50)]
    email: EmailStr
    photo: Optional[str] = None
    description: Optional[str] = None
    contact: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str):
        if v is not None and not re.fullmatch(r"[a-zA-Z0-9_]+", v):
            raise ValueError("username can only contain letters, numbers, and underscores")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str):
        if v is not None and not re.fullmatch(r"[A-Za-z ]+", v):
            raise ValueError("name can only contain letters and spaces")
        return v.strip() if v else v


class AdminCreate(AdminBase):
    password: str


class AdminUpdate(BaseModel):
    username: Optional[Annotated[str, Field(min_length=3, max_length=30)]] = None
    name: Optional[Annotated[str, Field(min_length=2, max_length=50)]] = None
    email: Optional[EmailStr] = None
    photo: Optional[str] = None
    description: Optional[str] = None
    contact: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str):
        if v is not None and not re.fullmatch(r"[a-zA-Z0-9_]+", v):
            raise ValueError("username can only contain letters, numbers, and underscores")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str):
        if v is not None and not re.fullmatch(r"[A-Za-z ]+", v):
            raise ValueError("name can only contain letters and spaces")
        return v.strip() if v else v


class AdminPublic(AdminBase):
    admin_id: Optional[Annotated[int, Field(gt=-1)]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AdminInDB(BaseModel):
    _id: Optional[str] = None
    admin_id: int
    username: str
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    photo: Optional[str]
    description: Optional[str]
    contact: str
    hashed_password: str



@router.get("/admins")
async def get_admin():
    admins = []
    cursor = admin_collection.find({})
    async for document in cursor:
        document["_id"] = str(document["_id"])
        admins.append(AdminPublic(**document))
    return admins


@router.get("/admins/{id}")
async def get_admin_by_id(id: int):
    admin_doc = await admin_collection.find_one({"admin_id": id})
    if not admin_doc:
        raise HTTPException(status_code=404, detail="Admin not found")
    admin_doc["_id"] = str(admin_doc["_id"])

    admin = AdminPublic(**admin_doc)
    return admin


@router.post("/admins")
async def post_admin(admin: AdminCreate):
    if await admin_collection.find_one({"username": admin.username}):
            raise HTTPException(status_code=400, detail="Username is already taken")

    last_admin = await admin_collection.find_one(
            sort=[("admin_id", -1)]
        )

    if last_admin is not None:
        new_admin_id = last_admin["admin_id"] + 1
    else:
        new_admin_id = 1

    document = admin.model_dump()
    document["admin_id"] = new_admin_id
    document["hashed_password"] = get_password_hash(document.pop("password"))
    document["created_at"] = datetime.utcnow()
    document["updated_at"] = datetime.utcnow()

    try:
        result = await admin_collection.insert_one(document)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Username is already taken")

    document["_id"] = str(result.inserted_id)
    document = AdminPublic(**document)

    return {
        "message": "Admin created successfully",
        "admin": document
    }


@router.patch("/admins/{id}")
async def patch_admin(id: int, data: AdminUpdate):
    updated_data = data.model_dump(exclude_unset=True)

    if not updated_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    updated_data["updated_at"] = datetime.utcnow()

    result = await admin_collection.update_one(
        {"admin_id": id},
        {"$set": updated_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Admin not found")

    document = await admin_collection.find_one({"admin_id": id})
    if document:
        document["_id"] = str(document["_id"])


    return {
            "message": "Admin updated successfully",
            "data": document
        }


@router.delete("/admins/{id}")
async def delete_admin(id: int):
    result = await admin_collection.delete_one({"admin_id": id})
    if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Admin not found")

    return {"message": "Admin deleted successfully"}
