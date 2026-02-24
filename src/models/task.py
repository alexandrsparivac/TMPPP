from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskType(Enum):
    ASSIGNMENT = "assignment"
    MEETING = "meeting"
    REMINDER = "reminder"
    PROJECT = "project"

@dataclass
class TaskMetadata:
    subject: Optional[str] = None
    estimated_duration: Optional[int] = None
    attachments: List[str] = field(default_factory=list)
    location: Optional[str] = None
    recurrence: Optional[Dict[str, Any]] = None
    priority_score: Optional[float] = None
    urgency_score: Optional[float] = None
    complexity_score: Optional[float] = None

@dataclass
class Task:
    id: Optional[str] = None
    user_id: str = ""
    title: str = ""
    description: str = ""
    type: TaskType = TaskType.ASSIGNMENT
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    deadline: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    metadata: TaskMetadata = field(default_factory=TaskMetadata)
    dependencies: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    calendar_event_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.title:
            raise ValueError("Task title cannot be empty")
        if self.user_id and not isinstance(self.user_id, str):
            raise TypeError("User ID must be a string")

    def update_status(self, new_status: TaskStatus) -> None:
        self.status = new_status
        self.updated_at = datetime.utcnow()
        if new_status == TaskStatus.COMPLETED:
            self.completed_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

    def add_dependency(self, task_id: str) -> None:
        if task_id and task_id not in self.dependencies:
            self.dependencies.append(task_id)
            self.updated_at = datetime.utcnow()

    def remove_dependency(self, task_id: str) -> None:
        if task_id in self.dependencies:
            self.dependencies.remove(task_id)
            self.updated_at = datetime.utcnow()

    def is_overdue(self) -> bool:
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline and self.status != TaskStatus.COMPLETED

    def days_until_deadline(self) -> Optional[int]:
        if not self.deadline:
            return None
        delta = self.deadline - datetime.utcnow()
        return delta.days

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "type": self.type.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "deadline": self.deadline,
            "tags": self.tags,
            "metadata": {
                "subject": self.metadata.subject,
                "estimated_duration": self.metadata.estimated_duration,
                "attachments": self.metadata.attachments,
                "location": self.metadata.location,
                "recurrence": self.metadata.recurrence,
                "priority_score": self.metadata.priority_score,
                "urgency_score": self.metadata.urgency_score,
                "complexity_score": self.metadata.complexity_score
            },
            "dependencies": self.dependencies,
            "subtasks": self.subtasks,
            "calendar_event_id": self.calendar_event_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        metadata_data = data.get("metadata", {})
        metadata = TaskMetadata(
            subject=metadata_data.get("subject"),
            estimated_duration=metadata_data.get("estimated_duration"),
            attachments=metadata_data.get("attachments", []),
            location=metadata_data.get("location"),
            recurrence=metadata_data.get("recurrence"),
            priority_score=metadata_data.get("priority_score"),
            urgency_score=metadata_data.get("urgency_score"),
            complexity_score=metadata_data.get("complexity_score")
        )

        return cls(
            id=data.get("id"),
            user_id=data.get("user_id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            type=TaskType(data.get("type", "assignment")),
            status=TaskStatus(data.get("status", "todo")),
            priority=TaskPriority(data.get("priority", "medium")),
            deadline=data.get("deadline"),
            tags=data.get("tags", []),
            metadata=metadata,
            dependencies=data.get("dependencies", []),
            subtasks=data.get("subtasks", []),
            calendar_event_id=data.get("calendar_event_id"),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow()),
            completed_at=data.get("completed_at")
        )

    def __str__(self) -> str:
        status_emoji = {
            TaskStatus.TODO: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.CANCELLED: "❌"
        }
        priority_emoji = {
            TaskPriority.LOW: "🟢",
            TaskPriority.MEDIUM: "🟡",
            TaskPriority.HIGH: "🟠",
            TaskPriority.URGENT: "🔴"
        }
        return f"{status_emoji[self.status]} {priority_emoji[self.priority]} {self.title}"

    def __repr__(self) -> str:
        return f"Task(id={self.id}, title='{self.title}', status={self.status.value}, priority={self.priority.value})"
