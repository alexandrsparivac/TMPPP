from abc import ABC, abstractmethod
from datetime import datetime

from src.models.task import Task, TaskPriority


class TaskSortStrategy(ABC):
    @abstractmethod
    def sort(self, tasks: list[Task]) -> list[Task]:
        pass


class DeadlineFirstStrategy(TaskSortStrategy):
    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda task: task.deadline or datetime.max)


class PriorityFirstStrategy(TaskSortStrategy):
    PRIORITY_ORDER = {
        TaskPriority.URGENT: 0,
        TaskPriority.HIGH: 1,
        TaskPriority.MEDIUM: 2,
        TaskPriority.LOW: 3,
    }

    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(
            tasks,
            key=lambda task: (self.PRIORITY_ORDER[task.priority], task.title.lower()),
        )


class SubjectStrategy(TaskSortStrategy):
    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(
            tasks,
            key=lambda task: (task.metadata.subject or "", task.title.lower()),
        )


class TaskListContext:
    """The /tasks command can change sorting behavior at runtime."""

    def __init__(self, strategy: TaskSortStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: TaskSortStrategy) -> None:
        self.strategy = strategy

    def ordered_tasks(self, tasks: list[Task]) -> list[Task]:
        return self.strategy.sort(tasks)
