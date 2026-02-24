import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from bson import ObjectId

from ..models.task import Task, TaskStatus, TaskType
from ..models.repositories import ITaskRepository

logger = logging.getLogger(__name__)

class MongoTaskRepository(ITaskRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        self._database = database
        self._collection: AsyncIOMotorCollection = database.tasks
        self._user_collection: AsyncIOMotorCollection = database.users

    async def create(self, task: Task) -> str:
        try:
            task_dict = task.to_dict()
            task_dict.pop("id", None)
            result = await self._collection.insert_one(task_dict)
            task_id = str(result.inserted_id)
            logger.info(f"✅ Created task: {task.title} (ID: {task_id})")
            return task_id
        except Exception as e:
            logger.error(f"❌ Failed to create task: {e}")
            raise

    async def update(self, task: Task) -> bool:
        try:
            if not task.id:
                logger.warning("⚠️ Cannot update task without ID")
                return False
            task_dict = task.to_dict()
            task_dict.pop("id", None)
            task_dict["updated_at"] = datetime.utcnow()
            result = await self._collection.update_one(
                {"_id": ObjectId(task.id)},
                {"$set": task_dict}
            )
            success = result.modified_count > 0
            if success:
                logger.info(f"✅ Updated task: {task.title}")
            else:
                logger.warning(f"⚠️ Task not found for update: {task.id}")
            return success
        except Exception as e:
            logger.error(f"❌ Failed to update task: {e}")
            raise

    async def delete(self, task_id: str) -> bool:
        try:
            result = await self._collection.delete_one({"_id": ObjectId(task_id)})
            success = result.deleted_count > 0
            if success:
                logger.info(f"🗑️ Deleted task: {task_id}")
            else:
                logger.warning(f"⚠️ Task not found for deletion: {task_id}")
            return success
        except Exception as e:
            logger.error(f"❌ Failed to delete task: {e}")
            raise

    async def get_by_id(self, task_id: str) -> Optional[Task]:
        try:
            task_doc = await self._collection.find_one({"_id": ObjectId(task_id)})
            if task_doc:
                task_doc["id"] = str(task_doc.pop("_id"))
                return Task.from_dict(task_doc)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get task by ID: {e}")
            raise

    async def get_user_tasks(
        self,
        user_id: str,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
        limit: int = 50
    ) -> List[Task]:
        try:
            query = {"user_id": user_id}
            if status:
                query["status"] = status.value
            if task_type:
                query["type"] = task_type.value
            cursor = self._collection.find(query).sort("deadline", 1).limit(limit)
            task_docs = await cursor.to_list(length=None)
            tasks = []
            for doc in task_docs:
                doc["id"] = str(doc.pop("_id"))
                tasks.append(Task.from_dict(doc))
            logger.info(f"📋 Retrieved {len(tasks)} tasks for user {user_id}")
            return tasks
        except Exception as e:
            logger.error(f"❌ Failed to get user tasks: {e}")
            raise

    async def get_upcoming_deadlines(self, user_id: str, days: int = 7) -> List[Task]:
        try:
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=days)
            query = {
                "user_id": user_id,
                "deadline": {"$gte": start_date, "$lte": end_date},
                "status": {"$ne": TaskStatus.COMPLETED.value}
            }
            cursor = self._collection.find(query).sort("deadline", 1)
            task_docs = await cursor.to_list(length=None)
            tasks = []
            for doc in task_docs:
                doc["id"] = str(doc.pop("_id"))
                tasks.append(Task.from_dict(doc))
            logger.info(f"📅 Found {len(tasks)} upcoming deadlines for user {user_id}")
            return tasks
        except Exception as e:
            logger.error(f"❌ Failed to get upcoming deadlines: {e}")
            raise

    async def search_tasks(self, user_id: str, search_term: str) -> List[Task]:
        try:
            query = {
                "user_id": user_id,
                "$or": [
                    {"title": {"$regex": search_term, "$options": "i"}},
                    {"description": {"$regex": search_term, "$options": "i"}}
                ]
            }
            cursor = self._collection.find(query).sort("created_at", -1)
            task_docs = await cursor.to_list(length=None)
            tasks = []
            for doc in task_docs:
                doc["id"] = str(doc.pop("_id"))
                tasks.append(Task.from_dict(doc))
            logger.info(f"🔍 Found {len(tasks)} tasks matching '{search_term}' for user {user_id}")
            return tasks
        except Exception as e:
            logger.error(f"❌ Failed to search tasks: {e}")
            raise

    async def get_overdue_tasks(self, user_id: str) -> List[Task]:
        try:
            query = {
                "user_id": user_id,
                "deadline": {"$lt": datetime.utcnow()},
                "status": {"$ne": TaskStatus.COMPLETED.value}
            }
            cursor = self._collection.find(query).sort("deadline", 1)
            task_docs = await cursor.to_list(length=None)
            tasks = []
            for doc in task_docs:
                doc["id"] = str(doc.pop("_id"))
                tasks.append(Task.from_dict(doc))
            logger.info(f"⚠️ Found {len(tasks)} overdue tasks for user {user_id}")
            return tasks
        except Exception as e:
            logger.error(f"❌ Failed to get overdue tasks: {e}")
            raise
