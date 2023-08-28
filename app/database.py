from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None

database = Database()

async def connect_to_mongodb():
    database.client = AsyncIOMotorClient(settings.MONGODB_URI)

async def close_mongodb_connection():
    database.client.close()

