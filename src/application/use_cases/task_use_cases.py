"""
Task Use Cases following SOLID principles
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ...core.entities.task import Task, TaskStatus, TaskType, TaskPriority
from ...core.entities.user import User
from ...core.interfaces.repositories import ITaskRepository, IUserRepository
from ...core.interfaces.services import INotificationService

logger = logging.getLogger(__name__)

class CreateTaskUseCase:
    """
    Use case for creating a task
    Following SOLID principles:
    - Single Responsibility: Only handles task creation
    - Open/Closed: Can be extended without modification
    - Liskov Substitution: Can replace any task creation use case
    - Interface Segregation: Depends only on needed interfaces
    - Dependency Inversion: Depends on abstractions
    """
    
    def __init__(
        self,
        task_repository: ITaskRepository,
        notification_service: INotificationService,
    ):
        self._task_repository = task_repository
        self._notification_service = notification_service
    
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
        """Execute task creation use case"""
        try:
            # Create task entity
            task = Task(
                user_id=user.id,
                title=title,
                description=description,
                type=task_type,
                priority=priority,
                deadline=deadline,
                tags=tags or []
            )
            
            # Validate task
            self._validate_task(task)
            
            # Save task
            task_id = await self._task_repository.create(task)
            task.id = task_id
            
            # Send notification
            if user.notifications_enabled():
                await self._notification_service.send_task_update_notification(
                    user, task, f"Task '{title}' created successfully"
                )
            
            logger.info(f"✅ Created task: {title} for user {user.id}")
            return task
            
        except Exception as e:
            logger.error(f"❌ Failed to create task: {e}")
            raise
    
    def _validate_task(self, task: Task) -> None:
        """Validate task data"""
        if not task.title.strip():
            raise ValueError("Task title cannot be empty")
        
        if task.deadline and task.deadline <= datetime.utcnow():
            raise ValueError("Deadline must be in the future")
        
        if len(task.title) > 200:
            raise ValueError("Task title too long (max 200 characters)")

class UpdateTaskUseCase:
    """
    Use case for updating a task
    Following SOLID principles
    """
    
    def __init__(
        self,
        task_repository: ITaskRepository,
        notification_service: INotificationService,
    ):
        self._task_repository = task_repository
        self._notification_service = notification_service
    
    async def execute(
        self,
        user: User,
        task_id: str,
        **updates
    ) -> Optional[Task]:
        """Execute task update use case"""
        try:
            # Get existing task
            task = await self._task_repository.get_by_id(task_id)
            if not task:
                logger.warning(f"⚠️ Task not found: {task_id}")
                return None
            
            # Verify ownership
            if task.user_id != user.id:
                logger.warning(f"⚠️ User {user.id} not authorized to update task {task_id}")
                return None
            
            # Apply updates
            original_status = task.status
            self._apply_updates(task, updates)
            
            # Validate updates
            self._validate_updates(task, updates)
            
            # Save task
            success = await self._task_repository.update(task)
            if not success:
                logger.error(f"❌ Failed to update task: {task_id}")
                return None
            
            # Send notification for status change
            if original_status != task.status and user.notifications_enabled():
                await self._notification_service.send_task_update_notification(
                    user, task, f"Task '{task.title}' status changed to {task.status.value}"
                )
            
            logger.info(f"✅ Updated task: {task_id}")
            return task
            
        except Exception as e:
            logger.error(f"❌ Failed to update task: {e}")
            raise
    
    def _apply_updates(self, task: Task, updates: Dict[str, Any]) -> None:
        """Apply updates to task"""
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
        """Validate task updates"""
        if "deadline" in updates and updates["deadline"]:
            if updates["deadline"] <= datetime.utcnow():
                raise ValueError("Deadline must be in the future")
        
        if "title" in updates and updates["title"]:
            if not updates["title"].strip():
                raise ValueError("Task title cannot be empty")
            if len(updates["title"]) > 200:
                raise ValueError("Task title too long (max 200 characters)")

class DeleteTaskUseCase:
    """
    Use case for deleting a task
    Following SOLID principles
    """
    
    def __init__(
        self,
        task_repository: ITaskRepository,
        notification_service: INotificationService,
    ):
        self._task_repository = task_repository
        self._notification_service = notification_service
    
    async def execute(self, user: User, task_id: str) -> bool:
        """Execute task deletion use case"""
        try:
            # Get existing task
            task = await self._task_repository.get_by_id(task_id)
            if not task:
                logger.warning(f"⚠️ Task not found: {task_id}")
                return False
            
            # Verify ownership
            if task.user_id != user.id:
                logger.warning(f"⚠️ User {user.id} not authorized to delete task {task_id}")
                return False
            
            # Delete task
            success = await self._task_repository.delete(task_id)
            if not success:
                logger.error(f"❌ Failed to delete task: {task_id}")
                return False
            
            # Send notification
            if user.notifications_enabled():
                await self._notification_service.send_task_update_notification(
                    user, task, f"Task '{task.title}' deleted"
                )
            
            logger.info(f"🗑️ Deleted task: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete task: {e}")
            raise

class GetTasksUseCase:
    """
    Use case for retrieving tasks
    Following SOLID principles
    """
    
    def __init__(self, task_repository: ITaskRepository):
        self._task_repository = task_repository
    
    async def execute(
        self,
        user: User,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
        limit: int = 50
    ) -> List[Task]:
        """Execute get tasks use case"""
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
        """Get upcoming deadlines"""
        try:
            tasks = await self._task_repository.get_upcoming_deadlines(user.id, days)
            
            logger.info(f"📅 Found {len(tasks)} upcoming deadlines for user {user.id}")
            return tasks
            
        except Exception as e:
            logger.error(f"❌ Failed to get upcoming deadlines: {e}")
            raise
    
    async def search_tasks(self, user: User, search_term: str) -> List[Task]:
        """Search tasks"""
        try:
            tasks = await self._task_repository.search_tasks(user.id, search_term)
            
            logger.info(f"🔍 Found {len(tasks)} tasks matching '{search_term}' for user {user.id}")
            return tasks
            
        except Exception as e:
            logger.error(f"❌ Failed to search tasks: {e}")
            raise
    
    async def get_overdue_tasks(self, user: User) -> List[Task]:
        """Get overdue tasks"""
        try:
            tasks = await self._task_repository.get_overdue_tasks(user.id)
            
            logger.info(f"⚠️ Found {len(tasks)} overdue tasks for user {user.id}")
            return tasks
            
        except Exception as e:
            logger.error(f"❌ Failed to get overdue tasks: {e}")
            raise
