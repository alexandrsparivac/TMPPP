"""
MongoDB Configuration for Student Life Helper Bot
"""
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/student_helper_bot")
DATABASE_NAME = "student_helper_bot"

# Async client for bot operations
async_client = AsyncIOMotorClient(MONGO_URI)
async_database = async_client[DATABASE_NAME]

# Sync client for admin operations
sync_client = MongoClient(MONGO_URI)
sync_database = sync_client[DATABASE_NAME]

# Collections
USERS_COLLECTION = "users"
TASKS_COLLECTION = "tasks"
PROJECTS_COLLECTION = "projects"
GOOGLE_SYNC_COLLECTION = "google_sync"
NOTIFICATIONS_COLLECTION = "notifications"

async def get_database():
    """Get async database instance"""
    return async_database

def get_sync_database():
    """Get sync database instance"""
    return sync_database

async def connect_to_mongo():
    """Connect to MongoDB"""
    try:
        # Test the connection
        await async_client.admin.command('ping')
        print("✅ Connected to MongoDB successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False

async def disconnect_from_mongo():
    """Disconnect from MongoDB"""
    async_client.close()
    print("🔌 Disconnected from MongoDB")

async def init_indexes():
    """Initialize database indexes for better performance"""
    db = await get_database()
    
    # Users collection indexes
    await db[USERS_COLLECTION].create_index("telegram_id", unique=True)
    await db[USERS_COLLECTION].create_index("email", unique=True, sparse=True)
    
    # Tasks collection indexes
    await db[TASKS_COLLECTION].create_index([("user_id", 1), ("deadline", 1)])
    await db[TASKS_COLLECTION].create_index("status")
    await db[TASKS_COLLECTION].create_index("priority")
    await db[TASKS_COLLECTION].create_index("tags")
    await db[TASKS_COLLECTION].create_index("type")
    
    # Projects collection indexes
    await db[PROJECTS_COLLECTION].create_index("user_id")
    await db[PROJECTS_COLLECTION].create_index("status")
    
    # Google sync collection indexes
    await db[GOOGLE_SYNC_COLLECTION].create_index([("user_id", 1), ("service", 1)])
    await db[GOOGLE_SYNC_COLLECTION].create_index("external_id")
    
    # Notifications collection indexes
    await db[NOTIFICATIONS_COLLECTION].create_index([("user_id", 1), ("created_at", -1)])
    await db[NOTIFICATIONS_COLLECTION].create_index("status")
    
    print("📊 Database indexes created successfully!")
