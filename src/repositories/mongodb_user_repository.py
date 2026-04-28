"""
MongoDB User Repository Implementation following SOLID principles
"""
import logging
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from bson import ObjectId

from ..models.user import User, UserRole
from ..models.repositories import IUserRepository

logger = logging.getLogger(__name__)

class MongoUserRepository(IUserRepository):
    """
    MongoDB implementation of IUserRepository
    Following SOLID principles:
    - Single Responsibility: Only handles MongoDB operations for users
    - Open/Closed: Open for extension but closed for modification
    - Liskov Substitution: Can replace any IUserRepository implementation
    - Interface Segregation: Implements only user-related methods
    - Dependency Inversion: Depends on IUserRepository abstraction
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self._database = database
        self._collection: AsyncIOMotorCollection = database.users
    
    async def create(self, user: User) -> str:
        """Create a new user in MongoDB"""
        try:
            user_dict = user.to_dict()
            user_dict.pop("id", None)  # Remove ID to let MongoDB generate it
            
            result = await self._collection.insert_one(user_dict)
            user_id = str(result.inserted_id)
            
            logger.info(f"✅ Created user: {user.full_name} (ID: {user_id})")
            return user_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create user: {e}")
            raise
    
    async def update(self, user: User) -> bool:
        """Update an existing user in MongoDB"""
        try:
            if not user.id:
                logger.warning("⚠️ Cannot update user without ID")
                return False
            
            user_dict = user.to_dict()
            user_dict["last_active"] = user.last_active
            
            result = await self._collection.update_one(
                {"_id": ObjectId(user.id)},
                {"$set": user_dict}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"✅ Updated user: {user.full_name}")
            else:
                logger.warning(f"⚠️ User not found for update: {user.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to update user: {e}")
            raise
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID from MongoDB"""
        try:
            user_doc = await self._collection.find_one({"_id": ObjectId(user_id)})
            
            if user_doc:
                user_doc["id"] = str(user_doc.pop("_id"))
                return User.from_dict(user_doc)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get user by ID: {e}")
            raise
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID from MongoDB"""
        try:
            user_doc = await self._collection.find_one({"telegram_id": telegram_id})
            
            if user_doc:
                user_doc["id"] = str(user_doc.pop("_id"))
                return User.from_dict(user_doc)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get user by Telegram ID: {e}")
            raise
    
    
    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        try:
            # Validate preferences
            valid_keys = [
                "notifications", "timezone", "language", "theme",
                "reminder_advance_hours", "daily_summary_enabled", "weekend_notifications"
            ]
            
            filtered_preferences = {k: v for k, v in preferences.items() if k in valid_keys}
            
            result = await self._collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "preferences": filtered_preferences,
                        "last_active": {"$currentDate": True}
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"✅ Updated preferences for user {user_id}")
            else:
                logger.warning(f"⚠️ User not found for preferences update: {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to update user preferences: {e}")
            raise
    
