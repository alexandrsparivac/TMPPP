"""
MongoDB Repositories for Student Life Helper Bot
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import ReturnDocument

from .models import Task, User, GoogleSync, Notification, PyObjectId

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.users
    
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        result = await self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user by Telegram ID"""
        user = await self.collection.find_one({"telegram_id": telegram_id})
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        return user
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data, "$currentDate": {"last_active": True}}
        )
        return result.modified_count > 0
    
    async def update_google_tokens(self, user_id: str, tokens: Dict[str, Any]) -> bool:
        """Update Google tokens for user"""
        return await self.update_user(user_id, {"google_tokens": tokens})
    
    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        return await self.update_user(user_id, {"preferences": preferences})

class TaskRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.tasks
    
    async def create_task(self, task_data: Dict[str, Any]) -> str:
        """Create a new task"""
        result = await self.collection.insert_one(task_data)
        return str(result.inserted_id)
    
    async def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        task = await self.collection.find_one({"_id": ObjectId(task_id)})
        return task
    
    async def get_user_tasks(
        self, 
        user_id: str, 
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get tasks for a user with optional filters"""
        query = {"user_id": ObjectId(user_id)}
        if status:
            query["status"] = status
        if task_type:
            query["type"] = task_type
        
        cursor = self.collection.find(query).sort("deadline", 1).limit(limit)
        return await cursor.to_list(length=None)
    
    async def get_upcoming_deadlines(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get tasks with deadlines in the next N days"""
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days)
        
        query = {
            "user_id": ObjectId(user_id),
            "deadline": {"$gte": start_date, "$lte": end_date},
            "status": {"$ne": "completed"}
        }
        
        cursor = self.collection.find(query).sort("deadline", 1)
        return await cursor.to_list(length=None)
    
    async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> bool:
        """Update task"""
        result = await self.collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {**update_data, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    async def update_task_status(self, task_id: str, new_status: str) -> bool:
        """Update task status"""
        return await self.update_task(task_id, {"status": new_status})
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        result = await self.collection.delete_one({"_id": ObjectId(task_id)})
        return result.deleted_count > 0
    
    async def search_tasks(self, user_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Search tasks by title or description"""
        query = {
            "user_id": ObjectId(user_id),
            "$or": [
                {"title": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}}
            ]
        }
        
        cursor = self.collection.find(query).sort("created_at", -1)
        return await cursor.to_list(length=None)

class GoogleSyncRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.google_sync
    
    async def create_sync_record(self, sync_data: Dict[str, Any]) -> str:
        """Create a new sync record"""
        result = await self.collection.insert_one(sync_data)
        return str(result.inserted_id)
    
    async def get_sync_by_external_id(self, user_id: str, service: str, external_id: str) -> Optional[Dict[str, Any]]:
        """Get sync record by external ID"""
        record = await self.collection.find_one({
            "user_id": ObjectId(user_id),
            "service": service,
            "external_id": external_id
        })
        return record
    
    async def update_sync_status(self, sync_id: str, status: str, error_message: str = None) -> bool:
        """Update sync status"""
        update_data = {
            "sync_status": status,
            "last_sync": datetime.utcnow()
        }
        if error_message:
            update_data["error_message"] = error_message
        
        result = await self.collection.update_one(
            {"_id": ObjectId(sync_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

class NotificationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.notifications
    
    async def create_notification(self, notification_data: Dict[str, Any]) -> str:
        """Create a new notification"""
        result = await self.collection.insert_one(notification_data)
        return str(result.inserted_id)
    
    async def get_pending_notifications(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get pending notifications to send"""
        query = {
            "status": "pending",
            "$or": [
                {"scheduled_at": {"$lte": datetime.utcnow()}},
                {"scheduled_at": None}
            ]
        }
        
        cursor = self.collection.find(query).sort("priority", -1).limit(limit)
        return await cursor.to_list(length=None)
    
    async def mark_notification_sent(self, notification_id: str) -> bool:
        """Mark notification as sent"""
        return await self.update_notification_status(notification_id, "sent")
    
    async def update_notification_status(self, notification_id: str, status: str) -> bool:
        """Update notification status"""
        update_data = {"status": status}
        if status == "sent":
            update_data["sent_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
