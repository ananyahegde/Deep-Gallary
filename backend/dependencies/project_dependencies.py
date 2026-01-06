from fastapi import HTTPException
from database import project_collection
from bson import ObjectId

async def get_project_by_id_or_404(id: str):
    try:
        project_doc = await project_collection.find_one({"_id": ObjectId(id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if not project_doc:
        raise HTTPException(status_code=404, detail="Project not found")

    project_doc["_id"] = str(project_doc["_id"])
    return project_doc
