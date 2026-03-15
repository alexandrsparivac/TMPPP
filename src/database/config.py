import os
import threading
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

USERS_COLLECTION = "users"
TASKS_COLLECTION = "tasks"


class DatabaseConnectionSingleton:

    _instance: Optional["DatabaseConnectionSingleton"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "DatabaseConnectionSingleton":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._client = None
        self._database = None
        self._mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/student_helper_bot")
        self._database_name = "student_helper_bot"
        self._is_connected = False

    @classmethod
    def get_instance(cls) -> "DatabaseConnectionSingleton":
        return cls()

    async def connect(self) -> bool:
        if self._is_connected:
            return True
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            self._client = AsyncIOMotorClient(self._mongo_uri)
            await self._client.admin.command("ping")
            self._database = self._client[self._database_name]
            self._is_connected = True
            logger.info("✅ DatabaseConnectionSingleton: connected to MongoDB")
            return True
        except Exception as e:
            logger.error(f"❌ DatabaseConnectionSingleton: connection failed: {e}")
            return False

    def disconnect(self) -> None:
        if self._client and self._is_connected:
            self._client.close()
            self._is_connected = False
            logger.info("🔌 DatabaseConnectionSingleton: disconnected")

    @property
    def database(self):
        if not self._is_connected:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._database

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    async def init_indexes(self) -> None:
        db = self.database
        await db[USERS_COLLECTION].create_index("telegram_id", unique=True)
        await db[TASKS_COLLECTION].create_index([("user_id", 1), ("deadline", 1)])
        await db[TASKS_COLLECTION].create_index("status")
        await db[TASKS_COLLECTION].create_index("priority")
        await db[TASKS_COLLECTION].create_index("tags")
        await db[TASKS_COLLECTION].create_index("type")


async def get_database():
    return DatabaseConnectionSingleton.get_instance().database

async def connect_to_mongo() -> bool:
    return await DatabaseConnectionSingleton.get_instance().connect()

def disconnect_from_mongo() -> None:
    DatabaseConnectionSingleton.get_instance().disconnect()
