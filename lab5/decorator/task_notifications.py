from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.models.task import Task
from src.models.user import User


@dataclass(frozen=True)
class ReminderMessage:
    user_id: str
    task_id: str | None
    title: str
    body: str


class TaskNotifier(ABC):
    @abstractmethod
    def send(self, message: ReminderMessage) -> list[str]:
        pass


class TelegramTaskNotifier(TaskNotifier):
    def __init__(self, chat_id: int):
        self.chat_id = chat_id

    def send(self, message: ReminderMessage) -> list[str]:
        return [f"telegram:{self.chat_id}:{message.title}"]


class TaskNotifierDecorator(TaskNotifier):
    def __init__(self, wrapped: TaskNotifier):
        self.wrapped = wrapped

    def send(self, message: ReminderMessage) -> list[str]:
        return self.wrapped.send(message)


class EmailTaskNotifierDecorator(TaskNotifierDecorator):
    def __init__(self, wrapped: TaskNotifier, email: str):
        super().__init__(wrapped)
        self.email = email

    def send(self, message: ReminderMessage) -> list[str]:
        deliveries = super().send(message)
        deliveries.append(f"email:{self.email}:{message.title}")
        return deliveries


class PushTaskNotifierDecorator(TaskNotifierDecorator):
    def __init__(self, wrapped: TaskNotifier, device_id: str):
        super().__init__(wrapped)
        self.device_id = device_id

    def send(self, message: ReminderMessage) -> list[str]:
        deliveries = super().send(message)
        deliveries.append(f"push:{self.device_id}:{message.title}")
        return deliveries


class DeadlineReminderMessageFactory:
    def create(self, user: User, task: Task) -> ReminderMessage:
        deadline = task.deadline.isoformat() if task.deadline else "no deadline"
        return ReminderMessage(
            user_id=user.id or "",
            task_id=task.id,
            title=f"Reminder: {task.title}",
            body=f"Deadline for '{task.title}': {deadline}",
        )
