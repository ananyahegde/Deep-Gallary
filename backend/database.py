import os
from dotenv import load_dotenv
import motor.motor_asyncio

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)

database = client.deep_gallary

admin_collection = database.admin
image_collection = database.image
project_collection = database.project

# def get_database():
#     return database

# async def close_mongo_connection():
#     client.close()
