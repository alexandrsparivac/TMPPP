"""
Service interfaces following Dependency Inversion Principle
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..entities.task import Task, TaskStatus
from ..entities.user import User

class INotificationService(ABC):
    """Notification service interface"""
    
    @abstractmethod
    async def send_deadline_notification(self, user: User, task: Task) -> bool:
        """Send deadline notification"""
        pass
    
    @abstractmethod
    async def send_task_update_notification(self, user: User, task: Task, message: str) -> bool:
        """Send task update notification"""
        pass
    
    @abstractmethod
    async def send_daily_summary(self, user: User, tasks: List[Task]) -> bool:
        """Send daily task summary"""
        pass


