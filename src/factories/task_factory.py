from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..models.task import Task, TaskType, TaskPriority


class TaskCreator(ABC):
    @abstractmethod
    def create_task(self, user_id: str, title: str, description: str = "",
                    priority: TaskPriority = TaskPriority.MEDIUM,
                    deadline: Optional[datetime] = None,
                    tags: Optional[List[str]] = None) -> Task:
        pass


class AssignmentTaskCreator(TaskCreator):
    def create_task(self, user_id: str, title: str, description: str = "",
                    priority: TaskPriority = TaskPriority.MEDIUM,
                    deadline: Optional[datetime] = None,
                    tags: Optional[List[str]] = None) -> Task:
        return Task(
            user_id=user_id, title=title, description=description,
            type=TaskType.ASSIGNMENT, priority=priority,
            deadline=deadline, tags=tags or []
        )


class MeetingTaskCreator(TaskCreator):
    def create_task(self, user_id: str, title: str, description: str = "",
                    priority: TaskPriority = TaskPriority.MEDIUM,
                    deadline: Optional[datetime] = None,
                    tags: Optional[List[str]] = None) -> Task:
        return Task(
            user_id=user_id, title=title, description=description,
            type=TaskType.MEETING, priority=priority,
            deadline=deadline, tags=tags or ["meeting"]
        )


class ReminderTaskCreator(TaskCreator):
    def create_task(self, user_id: str, title: str, description: str = "",
                    priority: TaskPriority = TaskPriority.MEDIUM,
                    deadline: Optional[datetime] = None,
                    tags: Optional[List[str]] = None) -> Task:
        return Task(
            user_id=user_id, title=title, description=description,
            type=TaskType.REMINDER, priority=priority,
            deadline=deadline, tags=tags or ["reminder"]
        )


class ProjectTaskCreator(TaskCreator):
    def create_task(self, user_id: str, title: str, description: str = "",
                    priority: TaskPriority = TaskPriority.MEDIUM,
                    deadline: Optional[datetime] = None,
                    tags: Optional[List[str]] = None) -> Task:
        return Task(
            user_id=user_id, title=title, description=description,
            type=TaskType.PROJECT, priority=priority,
            deadline=deadline, tags=tags or ["project"]
        )
