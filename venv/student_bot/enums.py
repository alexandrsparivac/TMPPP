
from enum import Enum


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class Recurrence(Enum):
    """Task recurrence."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class DocumentType(Enum):
    """Document type."""
    PDF = "pdf"
    COURSE = "course"
    ARTICLE = "article"
    NOTE = "note"
    OTHER = "other"
