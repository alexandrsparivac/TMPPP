from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @classmethod
    def from_text(cls, value: str) -> "Priority":
        normalized = value.strip().lower()
        aliases = {
            "mica": cls.LOW,
            "low": cls.LOW,
            "medie": cls.MEDIUM,
            "medium": cls.MEDIUM,
            "mare": cls.HIGH,
            "high": cls.HIGH,
            "urgent": cls.HIGH,
        }
        if normalized not in aliases:
            raise ValueError("Prioritatea trebuie sa fie low, medium sau high.")
        return aliases[normalized]


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

    @classmethod
    def from_text(cls, value: str) -> "TransactionType":
        normalized = value.strip().lower()
        aliases = {
            "income": cls.INCOME,
            "venit": cls.INCOME,
            "in": cls.INCOME,
            "expense": cls.EXPENSE,
            "cheltuiala": cls.EXPENSE,
            "out": cls.EXPENSE,
        }
        if normalized not in aliases:
            raise ValueError("Tipul trebuie sa fie income/venit sau expense/cheltuiala.")
        return aliases[normalized]


@dataclass(frozen=True)
class StudentProfile:
    name: str
    university: str
    faculty: str
    group: str
    year: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "university": self.university,
            "faculty": self.faculty,
            "group": self.group,
            "year": self.year,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "StudentProfile | None":
        if not data:
            return None
        return cls(
            name=str(data["name"]),
            university=str(data["university"]),
            faculty=str(data["faculty"]),
            group=str(data["group"]),
            year=int(data["year"]),
        )


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    due_date: date
    priority: Priority
    completed: bool
    created_at: datetime

    @property
    def short_id(self) -> str:
        return self.id.split("-")[0]

    def mark_completed(self) -> "Task":
        return Task(
            id=self.id,
            title=self.title,
            due_date=self.due_date,
            priority=self.priority,
            completed=True,
            created_at=self.created_at,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date.isoformat(),
            "priority": self.priority.value,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            due_date=date.fromisoformat(str(data["due_date"])),
            priority=Priority.from_text(str(data["priority"])),
            completed=bool(data["completed"]),
            created_at=datetime.fromisoformat(str(data["created_at"])),
        )


@dataclass(frozen=True)
class ScheduleEvent:
    id: str
    weekday: str
    time: str
    subject: str
    location: str

    @property
    def short_id(self) -> str:
        return self.id.split("-")[0]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "weekday": self.weekday,
            "time": self.time,
            "subject": self.subject,
            "location": self.location,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScheduleEvent":
        return cls(
            id=str(data["id"]),
            weekday=str(data["weekday"]),
            time=str(data["time"]),
            subject=str(data["subject"]),
            location=str(data["location"]),
        )


@dataclass(frozen=True)
class BudgetTransaction:
    id: str
    kind: TransactionType
    amount: float
    category: str
    description: str
    created_at: datetime

    @property
    def short_id(self) -> str:
        return self.id.split("-")[0]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind.value,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BudgetTransaction":
        return cls(
            id=str(data["id"]),
            kind=TransactionType.from_text(str(data["kind"])),
            amount=float(data["amount"]),
            category=str(data["category"]),
            description=str(data["description"]),
            created_at=datetime.fromisoformat(str(data["created_at"])),
        )


@dataclass(frozen=True)
class BudgetCategoryLimit:
    category: str
    monthly_limit: float
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "monthly_limit": self.monthly_limit,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BudgetCategoryLimit":
        return cls(
            category=str(data["category"]),
            monthly_limit=float(data["monthly_limit"]),
            created_at=datetime.fromisoformat(str(data["created_at"])),
        )


@dataclass(frozen=True)
class RecurringExpense:
    id: str
    amount: float
    category: str
    description: str
    day_of_month: int
    active: bool
    created_at: datetime

    @property
    def short_id(self) -> str:
        return self.id.split("-")[0]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "day_of_month": self.day_of_month,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecurringExpense":
        return cls(
            id=str(data["id"]),
            amount=float(data["amount"]),
            category=str(data["category"]),
            description=str(data["description"]),
            day_of_month=int(data["day_of_month"]),
            active=bool(data.get("active", True)),
            created_at=datetime.fromisoformat(str(data["created_at"])),
        )



@dataclass(frozen=True)
class Habit:
    id: str
    name: str
    log_dates: list[str]
    created_at: datetime

    @property
    def short_id(self) -> str:
        return self.id.split("-")[0]
        
    def log_today(self) -> "Habit":
        today_iso = date.today().isoformat()
        if today_iso not in self.log_dates:
            new_logs = self.log_dates + [today_iso]
            return Habit(id=self.id, name=self.name, log_dates=new_logs, created_at=self.created_at)
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "log_dates": self.log_dates,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Habit":
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            log_dates=list(data.get("log_dates", [])),
            created_at=datetime.fromisoformat(str(data["created_at"])),
        )

@dataclass(frozen=True)
class Note:

    id: str
    title: str
    body: str
    tag: str
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "tag": self.tag,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Note":
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            body=str(data["body"]),
            tag=str(data["tag"]),
            created_at=datetime.fromisoformat(str(data["created_at"])),
        )
