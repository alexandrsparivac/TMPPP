from dataclasses import dataclass

from src.models.task import Task, TaskPriority, TaskStatus


@dataclass(frozen=True)
class TaskBadge:
    status: TaskStatus
    priority: TaskPriority
    status_label: str
    priority_label: str

    def render(self) -> str:
        
        
        return f"[{self.status_label}/{self.priority_label}]"


class TaskBadgeFactory:
    """Flyweight factory for repeated task status and priority labels."""

    STATUS_LABELS = {
        TaskStatus.TODO: "todo",
        TaskStatus.IN_PROGRESS: "in-progress",
        TaskStatus.COMPLETED: "done",
        TaskStatus.CANCELLED: "cancelled",
    }
    PRIORITY_LABELS = {
        TaskPriority.LOW: "low",
        TaskPriority.MEDIUM: "medium",
        TaskPriority.HIGH: "high",
        TaskPriority.URGENT: "urgent",
    }

    def __init__(self):
        self._badges: dict[tuple[TaskStatus, TaskPriority], TaskBadge] = {}

    def get_badge(self, status: TaskStatus, priority: TaskPriority) -> TaskBadge:
        key = (status, priority)
        if key not in self._badges:
            self._badges[key] = TaskBadge(
                status=status,
                priority=priority,
                status_label=self.STATUS_LABELS[status],
                priority_label=self.PRIORITY_LABELS[priority],
            )
        return self._badges[key]

    def unique_badge_count(self) -> int:
        return len(self._badges)


@dataclass(frozen=True)
class RenderedTaskLine:
    task_id: str | None
    title: str
    badge: TaskBadge

    def as_text(self) -> str:
        return f"{self.badge.render()} {self.title}"


class TaskListRenderer:
    """Renders many bot task rows while sharing identical badge objects."""

    def __init__(self, badge_factory: TaskBadgeFactory):
        self.badge_factory = badge_factory

    def render(self, tasks: list[Task]) -> list[RenderedTaskLine]:
        return [
            RenderedTaskLine(
                task_id=task.id,
                title=task.title,
                badge=self.badge_factory.get_badge(task.status, task.priority),
            )
            for task in tasks
        ]
