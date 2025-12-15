from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from internal.admin import router as admin_router
from routers.image import router as image_router
from routers.project import router as project_router

app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Placeholder Method for Home Page"}

app.include_router(admin_router)
app.include_router(image_router)
app.include_router(project_router)
