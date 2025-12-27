from fastapi import HTTPException
from database import admin_collection

async def get_admin_or_404(id: int):
    admin_doc = await admin_collection.find_one({"admin_id": id})
    if not admin_doc:
        raise HTTPException(status_code=404, detail="Admin not found")
    admin_doc["_id"] = str(admin_doc["_id"])
    return admin_doc

async def verify_unique_username(username: str):
    if await admin_collection.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="Username is already taken")
