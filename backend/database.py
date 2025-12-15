import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')

database = client.deep_gallary

admin_collection = database.admin
image_collection = database.image
project_collection = database.project

# def get_database():
#     return database

# async def close_mongo_connection():
#     client.close()
