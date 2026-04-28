from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from .task import Task, TaskType, TaskStatus, TaskPriority, TaskMetadata


class ITaskBuilder(ABC):
    @abstractmethod
    def set_title(self, title: str) -> "ITaskBuilder":
        pass

    @abstractmethod
    def set_description(self, description: str) -> "ITaskBuilder":
        pass

    @abstractmethod
    def set_type(self, task_type: TaskType) -> "ITaskBuilder":
        pass

    @abstractmethod
    def set_priority(self, priority: TaskPriority) -> "ITaskBuilder":
        pass

    @abstractmethod
    def set_deadline(self, deadline: datetime) -> "ITaskBuilder":
        pass

    @abstractmethod
    def add_tag(self, tag: str) -> "ITaskBuilder":
        pass

    @abstractmethod
    def set_metadata(self, **kwargs) -> "ITaskBuilder":
        pass

    @abstractmethod
    def build(self) -> Task:
        pass


class TaskBuilder(ITaskBuilder):

    def __init__(self, user_id: str):
        self._user_id = user_id
        self._title = ""
        self._description = ""
        self._type = TaskType.ASSIGNMENT
        self._priority = TaskPriority.MEDIUM
        self._deadline: Optional[datetime] = None
        self._tags: List[str] = []
        self._metadata = TaskMetadata()
        self._dependencies: List[str] = []
        self._subtasks: List[str] = []

    def set_title(self, title: str) -> "TaskBuilder":
        self._title = title
        return self

    def set_description(self, description: str) -> "TaskBuilder":
        self._description = description
        return self

    def set_type(self, task_type: TaskType) -> "TaskBuilder":
        self._type = task_type
        return self

    def set_priority(self, priority: TaskPriority) -> "TaskBuilder":
        self._priority = priority
        return self

    def set_deadline(self, deadline: datetime) -> "TaskBuilder":
        self._deadline = deadline
        return self

    def add_tag(self, tag: str) -> "TaskBuilder":
        if tag and tag not in self._tags:
            self._tags.append(tag)
        return self

    def set_tags(self, tags: List[str]) -> "TaskBuilder":
        self._tags = list(tags)
        return self

    def set_metadata(self, **kwargs) -> "TaskBuilder":
        for key, value in kwargs.items():
            if hasattr(self._metadata, key):
                setattr(self._metadata, key, value)
        return self

    def add_dependency(self, task_id: str) -> "TaskBuilder":
        if task_id not in self._dependencies:
            self._dependencies.append(task_id)
        return self

    def add_subtask(self, subtask_id: str) -> "TaskBuilder":
        if subtask_id not in self._subtasks:
            self._subtasks.append(subtask_id)
        return self

    def build(self) -> Task:
        if not self._title.strip():
            raise ValueError("Task title is required")
        return Task(
            user_id=self._user_id,
            title=self._title,
            description=self._description,
            type=self._type,
            priority=self._priority,
            deadline=self._deadline,
            tags=self._tags.copy(),
            metadata=self._metadata,
            dependencies=self._dependencies.copy(),
            subtasks=self._subtasks.copy()
        )


class TaskDirector:

    def __init__(self, user_id: str):
        self._user_id = user_id

    def _builder(self) -> TaskBuilder:
        return TaskBuilder(self._user_id)

    def build_assignment(
        self,
        title: str,
        subject: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        deadline: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> Task:
        builder = (
            self._builder()
            .set_title(title)
            .set_type(TaskType.ASSIGNMENT)
            .set_priority(priority)
            .add_tag("assignment")
        )
        if subject:
            builder.set_metadata(subject=subject)
        if deadline:
            builder.set_deadline(deadline)
        for tag in (tags or []):
            builder.add_tag(tag)
        return builder.build()

    def build_meeting(
        self,
        title: str,
        location: Optional[str] = None,
        deadline: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> Task:
        builder = (
            self._builder()
            .set_title(title)
            .set_type(TaskType.MEETING)
            .set_priority(TaskPriority.HIGH)
            .add_tag("meeting")
        )
        if location:
            builder.set_metadata(location=location)
        if deadline:
            builder.set_deadline(deadline)
        for tag in (tags or []):
            builder.add_tag(tag)
        return builder.build()

    def build_project(
        self,
        title: str,
        description: str = "",
        deadline: Optional[datetime] = None,
        estimated_hours: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> Task:
        builder = (
            self._builder()
            .set_title(title)
            .set_description(description)
            .set_type(TaskType.PROJECT)
            .set_priority(TaskPriority.HIGH)
            .add_tag("project")
        )
        if estimated_hours:
            builder.set_metadata(estimated_duration=estimated_hours * 60)
        if deadline:
            builder.set_deadline(deadline)
        for tag in (tags or []):
            builder.add_tag(tag)
        return builder.build()

    def build_reminder(
        self,
        title: str,
        deadline: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> Task:
        builder = (
            self._builder()
            .set_title(title)
            .set_type(TaskType.REMINDER)
            .set_priority(TaskPriority.MEDIUM)
            .add_tag("reminder")
        )
        if deadline:
            builder.set_deadline(deadline)
        for tag in (tags or []):
            builder.add_tag(tag)
        return builder.build()

    def build_from_type(
        self,
        task_type: TaskType,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        deadline: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> Task:
        builder = (
            self._builder()
            .set_title(title)
            .set_description(description)
            .set_type(task_type)
            .set_priority(priority)
        )
        if deadline:
            builder.set_deadline(deadline)
        for tag in (tags or []):
            builder.add_tag(tag)
        return builder.build()
