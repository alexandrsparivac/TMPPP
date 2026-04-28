from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from .task import Task, TaskStatus, TaskType
from .user import User

class IRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Any]:
        pass

class ITaskRepository(IRepository):

    @abstractmethod
    async def create(self, task: Task) -> str:
        pass

    @abstractmethod
    async def update(self, task: Task) -> bool:
        pass

    @abstractmethod
    async def delete(self, task_id: str) -> bool:
        pass

    @abstractmethod
    async def get_by_id(self, task_id: str) -> Optional[Task]:
        pass

    @abstractmethod
    async def get_user_tasks(
        self,
        user_id: str,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
        limit: int = 50
    ) -> List[Task]:
        pass

    @abstractmethod
    async def get_upcoming_deadlines(self, user_id: str, days: int = 7) -> List[Task]:
        pass

    @abstractmethod
    async def search_tasks(self, user_id: str, search_term: str) -> List[Task]:
        pass

    @abstractmethod
    async def get_overdue_tasks(self, user_id: str) -> List[Task]:
        pass

class IUserRepository(IRepository):

    @abstractmethod
    async def create(self, user: User) -> str:
        pass

    @abstractmethod
    async def update(self, user: User) -> bool:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        pass
