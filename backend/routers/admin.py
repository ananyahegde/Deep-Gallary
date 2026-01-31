from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Annotated, Optional
import re
from database import admin_collection
from dependencies.admin_dependencies import (
    get_admin_by_field_or_404,
    verify_unique_username,
    verify_unique_email,
    save_admin_profile_image,
    delete_admin_profile_image
)
from dependencies.auth import get_password_hash, verify_password

router = APIRouter()

class AdminBase(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=30)]
    name: Annotated[str, Field(min_length=2, max_length=50)]
    email: str
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

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str):
        if v is not None and not re.fullmatch(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", v):
            raise ValueError("Not a valid email address")
        return v.strip() if v else v



class AdminCreate(AdminBase):
    password: str

@field_validator("password", mode="before")
@classmethod
def validate_password(cls, v: str):
    if not isinstance(v, str):
        raise ValueError("Password must be a string")

    v = v.strip()

    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", v):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"\d", v):
        raise ValueError("Password must contain at least one number")
    if not re.search(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~]", v):
        raise ValueError("Password must contain at least one special character")

    return v


class AdminUpdate(BaseModel):
    username: Optional[Annotated[str, Field(min_length=3, max_length=30)]] = None
    name: Optional[Annotated[str, Field(min_length=2, max_length=50)]] = None
    email: Optional[str] = None
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

    @field_validator("contact")
    @classmethod
    def validate_contact(cls, v: str):
        if not re.fullmatch(r"[0-9]{8,15}", v):
            raise ValueError("Contact must contain only digits (8–15 characters)")
        return v


class AdminPublic(AdminBase):
    admin_id: Optional[Annotated[int, Field(gt=-1)]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AdminInDB(BaseModel):
    _id: Optional[str] = None
    admin_id: int
    username: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime
    photo: Optional[str]
    description: Optional[str]
    contact: str
    hashed_password: str


@router.get("/admins")
async def get_admin(
    username: Optional[str] = None,
    email: Optional[str] = None
):
    admin_doc = await get_admin_by_field_or_404(username, email)

    if admin_doc:
        return [AdminPublic(**admin_doc)]

    admins = []
    cursor = admin_collection.find({})
    async for document in cursor:
        document["_id"] = str(document["_id"])
        admins.append(AdminPublic(**document))
    return admins


@router.post("/admins")
async def post_admin(
    username: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    contact: str = Form(...),
    description: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None)
):
    try:
        admin_data = AdminCreate(
            username=username,
            name=name,
            email=email,
            password=password,
            contact=contact,
            description=description
        )
    except ValidationError as e:
        cleaned_errors = []
        for err in e.errors():
            err = err.copy()
            # Remove non-JSON-serializable ctx
            if "ctx" in err:
                err["ctx"] = {
                    k: str(v) for k, v in err["ctx"].items()
                }
            cleaned_errors.append(err)

        raise HTTPException(status_code=422, detail=cleaned_errors)

    await verify_unique_username(admin_data.username)
    await verify_unique_email(admin_data.email)

    last_admin = await admin_collection.find_one(sort=[("admin_id", -1)])
    new_admin_id = last_admin["admin_id"] + 1 if last_admin else 1

    photo_path = None
    if photo:
        photo_path = await save_admin_profile_image(photo)

    document = admin_data.model_dump()
    document["admin_id"] = new_admin_id
    document["hashed_password"] = get_password_hash(document.pop("password"))
    document["photo"] = photo_path
    document["created_at"] = datetime.utcnow()
    document["updated_at"] = datetime.utcnow()

    try:
        result = await admin_collection.insert_one(document)
    except Exception:
        if photo_path:
            delete_admin_profile_image(photo_path)
        raise HTTPException(status_code=500, detail="Failed to create admin")

    document["_id"] = str(result.inserted_id)
    return {
        "message": "Admin created successfully",
        "admin": AdminPublic(**document)
    }


@router.patch("/admins")
async def patch_admin(
    username: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    new_username: Optional[str] = Form(None),
    new_email: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    contact: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
):
    if not username and not email:
        raise HTTPException(400, "Either username or email must be provided")

    admin_doc = await get_admin_by_field_or_404(username, email)
    if not admin_doc:
        raise HTTPException(404, "Admin not found")

    updated_data = {}

    if new_username and new_username != admin_doc["username"]:
        await verify_unique_username(new_username)
        updated_data["username"] = new_username

    if new_email and new_email != admin_doc["email"]:
        await verify_unique_email(new_email)
        updated_data["email"] = new_email

    if name and name != admin_doc.get("name"):
        updated_data["name"] = name

    if description is not None and description != admin_doc.get("description"):
        updated_data["description"] = description

    if contact and contact != admin_doc.get("contact"):
        updated_data["contact"] = contact

    if photo:
        new_photo_path = await save_admin_profile_image(photo)
        if admin_doc.get("photo"):
            delete_admin_profile_image(admin_doc["photo"])
        updated_data["photo"] = new_photo_path

    if not updated_data:
        raise HTTPException(400, "No fields provided for update")

    updated_data["updated_at"] = datetime.utcnow()

    await admin_collection.update_one(
        {"admin_id": admin_doc["admin_id"]},
        {"$set": updated_data}
    )

    document = await admin_collection.find_one({"admin_id": admin_doc["admin_id"]})
    if document:
        document["_id"] = str(document["_id"])

    return {"message": "Admin updated successfully", "data": document}


@router.delete("/admins")
async def delete_admin(
    password: str,
    username: Optional[str] = None,
    email: Optional[str] = None,
    admin_doc: dict = Depends(get_admin_by_field_or_404)
):
    if not username and not email:
        raise HTTPException(status_code=400, detail="Either username or email must be provided")

    if not verify_password(password, admin_doc["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")

    if admin_doc.get("photo"):
        delete_admin_profile_image(admin_doc["photo"])

    await admin_collection.delete_one({"admin_id": admin_doc["admin_id"]})
    return {"message": "Admin deleted successfully"}
