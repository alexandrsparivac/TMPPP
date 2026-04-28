from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.models.task import Task, TaskStatus


@dataclass(frozen=True)
class TaskEvent:
    task_id: str | None
    title: str
    event_type: str
    status: TaskStatus


class TaskObserver(ABC):
    @abstractmethod
    def update(self, event: TaskEvent) -> None:
        pass


class TaskEventSubject:
    def __init__(self):
        self._observers: list[TaskObserver] = []

    def attach(self, observer: TaskObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: TaskObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_task_changed(self, task: Task, event_type: str) -> None:
        event = TaskEvent(task.id, task.title, event_type, task.status)
        for observer in self._observers:
            observer.update(event)


class TelegramTaskObserver(TaskObserver):
    def __init__(self):
        self.messages: list[str] = []

    def update(self, event: TaskEvent) -> None:
        self.messages.append(f"Task {event.title}: {event.event_type}")


class AuditLogObserver(TaskObserver):
    def __init__(self):
        self.entries: list[TaskEvent] = []

    def update(self, event: TaskEvent) -> None:
        self.entries.append(event)


class CompletedTaskCounter(TaskObserver):
    def __init__(self):
        self.completed_count = 0

    def update(self, event: TaskEvent) -> None:
        if event.status == TaskStatus.COMPLETED:
            self.completed_count += 1
