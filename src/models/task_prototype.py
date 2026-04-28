import copy
from typing import Dict, List, Optional
from datetime import datetime

from .task import Task, TaskType, TaskPriority, TaskStatus, TaskMetadata


class TaskPrototypeRegistry:

    _prototypes: Dict[str, Task] = {}

    @classmethod
    def register(cls, name: str, prototype: Task) -> None:
        cls._prototypes[name] = prototype

    @classmethod
    def unregister(cls, name: str) -> None:
        cls._prototypes.pop(name, None)

    @classmethod
    def create_from(cls, name: str, user_id: str, title: str) -> Task:
        if name not in cls._prototypes:
            raise KeyError(f"Prototype '{name}' not registered")
        task = cls._prototypes[name].deep_clone()
        task.user_id = user_id
        task.title = title
        return task

    @classmethod
    def list_templates(cls) -> List[str]:
        return list(cls._prototypes.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        return name in cls._prototypes


def _init_default_prototypes() -> None:
    exam_proto = Task(
        user_id="prototype",
        title="Exam Template",
        description="Study all topics and complete practice exercises",
        type=TaskType.ASSIGNMENT,
        priority=TaskPriority.URGENT,
        tags=["exam", "study"],
        metadata=TaskMetadata(estimated_duration=180)
    )
    meeting_proto = Task(
        user_id="prototype",
        title="Meeting Template",
        description="Attend and participate in the scheduled meeting",
        type=TaskType.MEETING,
        priority=TaskPriority.HIGH,
        tags=["meeting"],
        metadata=TaskMetadata(estimated_duration=60)
    )
    homework_proto = Task(
        user_id="prototype",
        title="Homework Template",
        description="Complete and submit the homework assignment",
        type=TaskType.ASSIGNMENT,
        priority=TaskPriority.MEDIUM,
        tags=["homework", "assignment"],
        metadata=TaskMetadata(estimated_duration=90)
    )
    project_proto = Task(
        user_id="prototype",
        title="Project Template",
        description="Work on the project milestone and deliver the required output",
        type=TaskType.PROJECT,
        priority=TaskPriority.HIGH,
        tags=["project"],
        metadata=TaskMetadata(estimated_duration=300)
    )
    reminder_proto = Task(
        user_id="prototype",
        title="Reminder Template",
        description="Simple reminder",
        type=TaskType.REMINDER,
        priority=TaskPriority.MEDIUM,
        tags=["reminder"],
        metadata=TaskMetadata()
    )

    TaskPrototypeRegistry.register("exam", exam_proto)
    TaskPrototypeRegistry.register("meeting", meeting_proto)
    TaskPrototypeRegistry.register("homework", homework_proto)
    TaskPrototypeRegistry.register("project", project_proto)
    TaskPrototypeRegistry.register("reminder", reminder_proto)


_init_default_prototypes()
