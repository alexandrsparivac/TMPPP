import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/student_helper_bot")
DATABASE_NAME = "student_helper_bot"

async_client = AsyncIOMotorClient(MONGO_URI)
async_database = async_client[DATABASE_NAME]

USERS_COLLECTION = "users"
TASKS_COLLECTION = "tasks"

async def get_database():
    return async_database

async def connect_to_mongo():
    try:
        await async_client.admin.command('ping')
        print("✅ Connected to MongoDB successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False

async def disconnect_from_mongo():
    async_client.close()
    print("🔌 Disconnected from MongoDB")

async def init_indexes():
    db = await get_database()
    await db[USERS_COLLECTION].create_index("telegram_id", unique=True)
    await db[TASKS_COLLECTION].create_index([("user_id", 1), ("deadline", 1)])
    await db[TASKS_COLLECTION].create_index("status")
    await db[TASKS_COLLECTION].create_index("priority")
    await db[TASKS_COLLECTION].create_index("tags")
    await db[TASKS_COLLECTION].create_index("type")
