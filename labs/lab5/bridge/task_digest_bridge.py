from abc import ABC, abstractmethod

from src.models.task import Task
from src.models.user import User


class DeliveryChannel(ABC):
    @abstractmethod
    def deliver(self, user: User, subject: str, body: str) -> str:
        pass


class TelegramChannel(DeliveryChannel):
    def deliver(self, user: User, subject: str, body: str) -> str:
        return f"telegram:{user.telegram_id}:{subject}:{body}"


class EmailChannel(DeliveryChannel):
    def deliver(self, user: User, subject: str, body: str) -> str:
        if not user.email:
            raise ValueError("User email is required")
        return f"email:{user.email}:{subject}:{body}"


class TaskDigest(ABC):
    """Abstraction that is independent from the delivery implementation."""

    def __init__(self, tasks: list[Task], channel: DeliveryChannel):
        self.tasks = tasks
        self.channel = channel

    def send_to(self, user: User) -> str:
        return self.channel.deliver(user, self.subject(), self.body())

    @abstractmethod
    def subject(self) -> str:
        pass

    @abstractmethod
    def body(self) -> str:
        pass


class DailySummaryDigest(TaskDigest):
    def subject(self) -> str:
        return "Daily task summary"

    def body(self) -> str:
        return f"You have {len(self.tasks)} tasks today"


class DeadlineDigest(TaskDigest):
    def subject(self) -> str:
        return "Upcoming deadlines"

    def body(self) -> str:
        titles = ", ".join(task.title for task in self.tasks)
        return f"Deadlines: {titles}" if titles else "No deadlines"
