"""
Repository interfaces following Dependency Inversion Principle
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..entities.task import Task, TaskStatus, TaskType
from ..entities.user import User

class IRepository(ABC):
    """Base repository interface"""
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Any]:
        """Get entity by ID"""
        pass

class ITaskRepository(IRepository):
    """Task repository interface following Interface Segregation Principle"""
    
    @abstractmethod
    async def create(self, task: Task) -> str:
        """Create a new task"""
        pass
    
    @abstractmethod
    async def update(self, task: Task) -> bool:
        """Update an existing task"""
        pass
    
    @abstractmethod
    async def delete(self, task_id: str) -> bool:
        """Delete a task"""
        pass
    
    @abstractmethod
    async def get_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        pass
    
    @abstractmethod
    async def get_user_tasks(
        self, 
        user_id: str, 
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
        limit: int = 50
    ) -> List[Task]:
        """Get tasks for a user with optional filters"""
        pass
    
    @abstractmethod
    async def get_upcoming_deadlines(self, user_id: str, days: int = 7) -> List[Task]:
        """Get tasks with deadlines in the next N days"""
        pass
    
    @abstractmethod
    async def search_tasks(self, user_id: str, search_term: str) -> List[Task]:
        """Search tasks by title or description"""
        pass
    
    @abstractmethod
    async def get_overdue_tasks(self, user_id: str) -> List[Task]:
        """Get overdue tasks for a user"""
        pass

class IUserRepository(IRepository):
    """User repository interface following Interface Segregation Principle"""
    
    @abstractmethod
    async def create(self, user: User) -> str:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> bool:
        """Update an existing user"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        pass
    
    @abstractmethod
    async def update_google_tokens(self, user_id: str, tokens: Dict[str, Any]) -> bool:
        """Update Google tokens"""
        pass
    
    @abstractmethod
    async def get_active_users_count(self) -> int:
        """Get count of active users"""
        pass

class INotificationRepository(IRepository):
    """Notification repository interface"""
    
    @abstractmethod
    async def create_notification(self, notification_data: Dict[str, Any]) -> str:
        """Create a new notification"""
        pass
    
    @abstractmethod
    async def get_pending_notifications(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get pending notifications to send"""
        pass
    
    @abstractmethod
    async def mark_as_sent(self, notification_id: str) -> bool:
        """Mark notification as sent"""
        pass
    
    @abstractmethod
    async def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        pass

class IGoogleSyncRepository(IRepository):
    """Google sync repository interface"""
    
    @abstractmethod
    async def create_sync_record(self, sync_data: Dict[str, Any]) -> str:
        """Create a new sync record"""
        pass
    
    @abstractmethod
    async def get_sync_by_external_id(
        self, 
        user_id: str, 
        service: str, 
        external_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get sync record by external ID"""
        pass
    
    @abstractmethod
    async def update_sync_status(
        self, 
        sync_id: str, 
        status: str, 
        error_message: str = None
    ) -> bool:
        """Update sync status"""
        pass
    
    @abstractmethod
    async def get_pending_syncs(self, service: str) -> List[Dict[str, Any]]:
        """Get pending sync records for a service"""
        pass
