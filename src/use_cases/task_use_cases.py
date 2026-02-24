import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..models.task import Task, TaskStatus, TaskType, TaskPriority
from ..models.user import User
from ..models.repositories import ITaskRepository, IUserRepository

logger = logging.getLogger(__name__)

class CreateTaskUseCase:

    def __init__(self, task_repository: ITaskRepository):
        self._task_repository = task_repository

    async def execute(
        self,
        user: User,
        title: str,
        description: str = "",
        task_type: TaskType = TaskType.ASSIGNMENT,
        priority: TaskPriority = TaskPriority.MEDIUM,
        deadline: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> Task:
        try:
            task = Task(
                user_id=user.id,
                title=title,
                description=description,
                type=task_type,
                priority=priority,
                deadline=deadline,
                tags=tags or []
            )

            self._validate_task(task)

            task_id = await self._task_repository.create(task)
            task.id = task_id

            logger.info(f"✅ Created task: {title} for user {user.id}")
            return task

        except Exception as e:
            logger.error(f"❌ Failed to create task: {e}")
            raise

    def _validate_task(self, task: Task) -> None:
        if not task.title.strip():
            raise ValueError("Task title cannot be empty")
        if task.deadline and task.deadline <= datetime.utcnow():
            raise ValueError("Deadline must be in the future")
        if len(task.title) > 200:
            raise ValueError("Task title too long (max 200 characters)")

class UpdateTaskUseCase:

    def __init__(self, task_repository: ITaskRepository):
        self._task_repository = task_repository

    async def execute(self, user: User, task_id: str, **updates) -> Optional[Task]:
        try:
            task = await self._task_repository.get_by_id(task_id)
            if not task:
                logger.warning(f"⚠️ Task not found: {task_id}")
                return None

            if task.user_id != user.id:
                logger.warning(f"⚠️ User {user.id} not authorized to update task {task_id}")
                return None

            self._apply_updates(task, updates)
            self._validate_updates(task, updates)

            success = await self._task_repository.update(task)
            if not success:
                logger.error(f"❌ Failed to update task: {task_id}")
                return None

            logger.info(f"✅ Updated task: {task_id}")
            return task

        except Exception as e:
            logger.error(f"❌ Failed to update task: {e}")
            raise

    def _apply_updates(self, task: Task, updates: Dict[str, Any]) -> None:
        for key, value in updates.items():
            if hasattr(task, key):
                if key == "status" and isinstance(value, str):
                    task.update_status(TaskStatus(value))
                elif key == "type" and isinstance(value, str):
                    task.type = TaskType(value)
                elif key == "priority" and isinstance(value, str):
                    task.priority = TaskPriority(value)
                else:
                    setattr(task, key, value)

    def _validate_updates(self, task: Task, updates: Dict[str, Any]) -> None:
        if "deadline" in updates and updates["deadline"]:
            if updates["deadline"] <= datetime.utcnow():
                raise ValueError("Deadline must be in the future")
        if "title" in updates and updates["title"]:
            if not updates["title"].strip():
                raise ValueError("Task title cannot be empty")
            if len(updates["title"]) > 200:
                raise ValueError("Task title too long (max 200 characters)")

class DeleteTaskUseCase:

    def __init__(self, task_repository: ITaskRepository):
        self._task_repository = task_repository

    async def execute(self, user: User, task_id: str) -> bool:
        try:
            task = await self._task_repository.get_by_id(task_id)
            if not task:
                logger.warning(f"⚠️ Task not found: {task_id}")
                return False

            if task.user_id != user.id:
                logger.warning(f"⚠️ User {user.id} not authorized to delete task {task_id}")
                return False

            success = await self._task_repository.delete(task_id)
            if not success:
                logger.error(f"❌ Failed to delete task: {task_id}")
                return False

            logger.info(f"🗑️ Deleted task: {task_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete task: {e}")
            raise

class GetTasksUseCase:

    def __init__(self, task_repository: ITaskRepository):
        self._task_repository = task_repository

    async def execute(
        self,
        user: User,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
        limit: int = 50
    ) -> List[Task]:
        try:
            tasks = await self._task_repository.get_user_tasks(
                user.id, status, task_type, limit
            )
            logger.info(f"📋 Retrieved {len(tasks)} tasks for user {user.id}")
            return tasks
        except Exception as e:
            logger.error(f"❌ Failed to get tasks: {e}")
            raise

    async def get_upcoming_deadlines(self, user: User, days: int = 7) -> List[Task]:
        try:
            tasks = await self._task_repository.get_upcoming_deadlines(user.id, days)
            logger.info(f"📅 Found {len(tasks)} upcoming deadlines for user {user.id}")
            return tasks
        except Exception as e:
            logger.error(f"❌ Failed to get upcoming deadlines: {e}")
            raise

    async def search_tasks(self, user: User, search_term: str) -> List[Task]:
        try:
            tasks = await self._task_repository.search_tasks(user.id, search_term)
            logger.info(f"🔍 Found {len(tasks)} tasks matching '{search_term}' for user {user.id}")
            return tasks
        except Exception as e:
            logger.error(f"❌ Failed to search tasks: {e}")
            raise

    async def get_overdue_tasks(self, user: User) -> List[Task]:
        try:
            tasks = await self._task_repository.get_overdue_tasks(user.id)
            logger.info(f"⚠️ Found {len(tasks)} overdue tasks for user {user.id}")
            return tasks
        except Exception as e:
            logger.error(f"❌ Failed to get overdue tasks: {e}")
            raise
