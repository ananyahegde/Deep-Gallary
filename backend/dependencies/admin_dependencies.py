from fastapi import HTTPException
from database import admin_collection
from typing import Optional

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
