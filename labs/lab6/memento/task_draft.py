from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class TaskDraftMemento:
    title: str
    description: str
    tags: tuple[str, ...]
    deadline: datetime | None


@dataclass
class TaskDraft:
    """Conversation state while a user fills /add_task details."""

    title: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    deadline: datetime | None = None

    def set_title(self, title: str) -> None:
        self.title = title

    def set_description(self, description: str) -> None:
        self.description = description

    def add_tag(self, tag: str) -> None:
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def set_deadline(self, deadline: datetime | None) -> None:
        self.deadline = deadline

    def save(self) -> TaskDraftMemento:
        return TaskDraftMemento(
            title=self.title,
            description=self.description,
            tags=tuple(self.tags),
            deadline=self.deadline,
        )

    def restore(self, memento: TaskDraftMemento) -> None:
        self.title = memento.title
        self.description = memento.description
        self.tags = list(memento.tags)
        self.deadline = memento.deadline


class DraftHistory:
    def __init__(self):
        self._versions: list[TaskDraftMemento] = []

    def push(self, memento: TaskDraftMemento) -> None:
        self._versions.append(memento)

    def pop(self) -> TaskDraftMemento:
        if not self._versions:
            raise IndexError("No draft versions saved")
        return self._versions.pop()

    def count(self) -> int:
        return len(self._versions)
