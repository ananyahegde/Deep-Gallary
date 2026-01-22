import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers.admin import router as admin_router
from routers.image import router as image_router
from routers.project import router as project_router
from dependencies.auth import router as auth_router

app = FastAPI()

origins = ["http://localhost:3000", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/uploads", StaticFiles(directory=str(BASE_DIR / "uploads")), name="uploads")

@app.get("/")
def read_root():
    return {"Placeholder Method for Home Page"}

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(image_router)
app.include_router(project_router)
