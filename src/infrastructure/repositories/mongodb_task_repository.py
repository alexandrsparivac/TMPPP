"""
MongoDB Task Repository Implementation following SOLID principles
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from bson import ObjectId

from ...core.entities.task import Task, TaskStatus, TaskType
from ...core.interfaces.repositories import ITaskRepository

logger = logging.getLogger(__name__)

class MongoTaskRepository(ITaskRepository):
    """
    MongoDB implementation of ITaskRepository
    Following SOLID principles:
    - Single Responsibility: Only handles MongoDB operations for tasks
    - Open/Closed: Open for extension but closed for modification
    - Liskov Substitution: Can replace any ITaskRepository implementation
    - Interface Segregation: Implements only task-related methods
    - Dependency Inversion: Depends on ITaskRepository abstraction
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self._database = database
        self._collection: AsyncIOMotorCollection = database.tasks
        self._user_collection: AsyncIOMotorCollection = database.users
    
    async def create(self, task: Task) -> str:
        """Create a new task in MongoDB"""
        try:
            task_dict = task.to_dict()
            task_dict.pop("id", None)  # Remove ID to let MongoDB generate it
            
            result = await self._collection.insert_one(task_dict)
            task_id = str(result.inserted_id)
            
            logger.info(f"✅ Created task: {task.title} (ID: {task_id})")
            return task_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create task: {e}")
            raise
    
    async def update(self, task: Task) -> bool:
        """Update an existing task in MongoDB"""
        try:
            if not task.id:
                logger.warning("⚠️ Cannot update task without ID")
                return False
            
            task_dict = task.to_dict()
            task_dict.pop("id", None)  # Remove 'id' - MongoDB uses '_id'
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
        """Delete a task from MongoDB"""
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
        """Get task by ID from MongoDB"""
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
        """Get tasks for a user with optional filters"""
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
        """Get tasks with deadlines in the next N days"""
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
        """Search tasks by title or description"""
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
        """Get overdue tasks for a user"""
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
    
    async def get_task_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get task statistics for a user"""
        try:
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": None,
                    "total_tasks": {"$sum": 1},
                    "completed_tasks": {
                        "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                    },
                    "overdue_tasks": {
                        "$sum": {"$cond": [
                            {"$and": [
                                {"$lt": ["$deadline", datetime.utcnow()]},
                                {"$ne": ["$status", "completed"]}
                            ]}, 1, 0
                        ]}
                    },
                    "by_status": {
                        "$push": "$status"
                    },
                    "by_priority": {
                        "$push": "$priority"
                    }
                }}
            ]
            
            result = await self._collection.aggregate(pipeline).to_list(length=1)
            
            if result:
                stats = result[0]
                status_counts = {}
                for status in stats["by_status"]:
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                priority_counts = {}
                for priority in stats["by_priority"]:
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                return {
                    "total_tasks": stats["total_tasks"],
                    "completed_tasks": stats["completed_tasks"],
                    "overdue_tasks": stats["overdue_tasks"],
                    "completion_rate": (
                        stats["completed_tasks"] / stats["total_tasks"] * 100 
                        if stats["total_tasks"] > 0 else 0
                    ),
                    "status_distribution": status_counts,
                    "priority_distribution": priority_counts
                }
            
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "overdue_tasks": 0,
                "completion_rate": 0,
                "status_distribution": {},
                "priority_distribution": {}
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get task statistics: {e}")
            raise
