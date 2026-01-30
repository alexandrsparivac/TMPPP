from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import uuid

from .enums import Priority, TaskStatus, Recurrence, DocumentType


@dataclass
class BaseEntity:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class User(BaseEntity):
    telegram_id: int = 0
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    google_token: Optional[str] = None
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Topic(BaseEntity):
    name: str = ""
    parent_topic_id: Optional[str] = None
    description: str = ""


@dataclass
class Task(BaseEntity):
    name: str = ""
    topic_id: Optional[str] = None
    subtopic_id: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    recurrence: Recurrence = Recurrence.NONE
    description: str = ""
    user_id: str = ""


@dataclass
class Test(BaseEntity):
    title: str = ""
    subject: str = ""
    scheduled_date: Optional[datetime] = None
    duration_minutes: int = 60
    location: str = ""
    notes: str = ""
    is_done: bool = False
    user_id: str = ""


@dataclass
class Document(BaseEntity):
    title: str = ""
    document_type: DocumentType = DocumentType.OTHER
    subject: str = ""
    link: str = ""
    file_path: Optional[str] = None
    description: str = ""
    user_id: str = ""
