from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

from .models import (
    BudgetCategoryLimit,
    BudgetTransaction,
    Habit,
    Note,
    Priority,
    RecurringExpense,
    ScheduleEvent,
    StudentProfile,
    Task,
    TransactionType,
)


class StudentProfileBuilder:
    """Builder: validates and builds a profile step by step."""

    def __init__(self) -> None:
        self._name: str | None = None
        self._university: str | None = None
        self._faculty: str | None = None
        self._group: str | None = None
        self._year: int | None = None

    def named(self, name: str) -> "StudentProfileBuilder":
        self._name = self._required(name, "Numele este obligatoriu.")
        return self

    def at_university(self, university: str) -> "StudentProfileBuilder":
        self._university = self._required(university, "Universitatea este obligatorie.")
        return self

    def in_faculty(self, faculty: str) -> "StudentProfileBuilder":
        self._faculty = self._required(faculty, "Facultatea este obligatorie.")
        return self

    def in_group(self, group: str) -> "StudentProfileBuilder":
        self._group = self._required(group, "Grupa este obligatorie.")
        return self

    def in_year(self, year: int | str) -> "StudentProfileBuilder":
        parsed = int(year)
        if parsed < 1 or parsed > 8:
            raise ValueError("Anul de studii trebuie sa fie intre 1 si 8.")
        self._year = parsed
        return self

    def build(self) -> StudentProfile:
        missing = [
            label
            for label, value in {
                "nume": self._name,
                "universitate": self._university,
                "facultate": self._faculty,
                "grupa": self._group,
                "an": self._year,
            }.items()
            if value is None
        ]
        if missing:
            raise ValueError("Lipsesc campuri pentru profil: " + ", ".join(missing))
        return StudentProfile(
            name=self._name or "",
            university=self._university or "",
            faculty=self._faculty or "",
            group=self._group or "",
            year=self._year or 1,
        )

    @staticmethod
    def _required(value: str, message: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(message)
        return cleaned


class TaskBuilder:
    """Builder: keeps task validation away from command parsing."""

    def __init__(self) -> None:
        self._title: str | None = None
        self._due_date: date | None = None
        self._priority = Priority.MEDIUM

    def titled(self, title: str) -> "TaskBuilder":
        cleaned = title.strip()
        if len(cleaned) < 3:
            raise ValueError("Titlul taskului trebuie sa aiba minim 3 caractere.")
        self._title = cleaned
        return self

    def due_on(self, value: str | date) -> "TaskBuilder":
        if isinstance(value, date):
            parsed = value
        else:
            parsed = date.fromisoformat(value.strip())
        self._due_date = parsed
        return self

    def with_priority(self, priority: str | Priority) -> "TaskBuilder":
        self._priority = priority if isinstance(priority, Priority) else Priority.from_text(priority)
        return self

    def build(self) -> Task:
        if self._title is None:
            raise ValueError("Titlul taskului este obligatoriu.")
        if self._due_date is None:
            raise ValueError("Data limita este obligatorie.")
        return Task(
            id=str(uuid4()),
            title=self._title,
            due_date=self._due_date,
            priority=self._priority,
            completed=False,
            created_at=datetime.now(),
        )


class ScheduleEventBuilder:
    """Builder: creates a schedule item with a consistent format."""

    def __init__(self) -> None:
        self._weekday: str | None = None
        self._time: str | None = None
        self._subject: str | None = None
        self._location: str | None = None

    def on_weekday(self, weekday: str) -> "ScheduleEventBuilder":
        cleaned = weekday.strip().capitalize()
        if not cleaned:
            raise ValueError("Ziua este obligatorie.")
        self._weekday = cleaned
        return self

    def at_time(self, time_value: str) -> "ScheduleEventBuilder":
        cleaned = time_value.strip()
        if len(cleaned) != 5 or cleaned[2] != ":":
            raise ValueError("Ora trebuie scrisa in format HH:MM.")
        self._time = cleaned
        return self

    def for_subject(self, subject: str) -> "ScheduleEventBuilder":
        cleaned = subject.strip()
        if not cleaned:
            raise ValueError("Materia este obligatorie.")
        self._subject = cleaned
        return self

    def in_location(self, location: str) -> "ScheduleEventBuilder":
        cleaned = location.strip() or "Nespecificat"
        self._location = cleaned
        return self

    def build(self) -> ScheduleEvent:
        if None in (self._weekday, self._time, self._subject, self._location):
            raise ValueError("Evenimentul din orar nu este complet.")
        return ScheduleEvent(
            id=str(uuid4()),
            weekday=self._weekday or "",
            time=self._time or "",
            subject=self._subject or "",
            location=self._location or "",
        )


class BudgetTransactionBuilder:
    """Builder: prevents invalid money records from reaching storage."""

    def __init__(self) -> None:
        self._kind: TransactionType | None = None
        self._amount: float | None = None
        self._category: str | None = None
        self._description: str | None = None

    def of_type(self, kind: str | TransactionType) -> "BudgetTransactionBuilder":
        self._kind = kind if isinstance(kind, TransactionType) else TransactionType.from_text(kind)
        return self

    def with_amount(self, amount: str | float) -> "BudgetTransactionBuilder":
        parsed = float(str(amount).replace(",", "."))
        if parsed <= 0:
            raise ValueError("Suma trebuie sa fie mai mare decat 0.")
        self._amount = parsed
        return self

    def in_category(self, category: str) -> "BudgetTransactionBuilder":
        cleaned = category.strip()
        if not cleaned:
            raise ValueError("Categoria este obligatorie.")
        self._category = cleaned
        return self

    def described_as(self, description: str) -> "BudgetTransactionBuilder":
        self._description = description.strip() or "Fara descriere"
        return self

    def build(self) -> BudgetTransaction:
        if None in (self._kind, self._amount, self._category, self._description):
            raise ValueError("Tranzactia nu este completa.")
        return BudgetTransaction(
            id=str(uuid4()),
            kind=self._kind or TransactionType.EXPENSE,
            amount=self._amount or 0.0,
            category=self._category or "",
            description=self._description or "",
            created_at=datetime.now(),
        )


class BudgetCategoryLimitBuilder:
    """Builder: validates monthly category limits."""

    def __init__(self) -> None:
        self._category: str | None = None
        self._monthly_limit: float | None = None

    def in_category(self, category: str) -> "BudgetCategoryLimitBuilder":
        cleaned = category.strip().lower()
        if not cleaned:
            raise ValueError("Categoria este obligatorie.")
        self._category = cleaned
        return self

    def with_monthly_limit(self, amount: str | float) -> "BudgetCategoryLimitBuilder":
        parsed = float(str(amount).replace(",", "."))
        if parsed <= 0:
            raise ValueError("Limita trebuie sa fie mai mare decat 0.")
        self._monthly_limit = parsed
        return self

    def build(self) -> BudgetCategoryLimit:
        if self._category is None or self._monthly_limit is None:
            raise ValueError("Limita bugetara nu este completa.")
        return BudgetCategoryLimit(
            category=self._category,
            monthly_limit=self._monthly_limit,
            created_at=datetime.now(),
        )


class RecurringExpenseBuilder:
    """Builder: validates monthly recurring expenses."""

    def __init__(self) -> None:
        self._amount: float | None = None
        self._category: str | None = None
        self._description: str | None = None
        self._day_of_month: int | None = None

    def with_amount(self, amount: str | float) -> "RecurringExpenseBuilder":
        parsed = float(str(amount).replace(",", "."))
        if parsed <= 0:
            raise ValueError("Suma recurenta trebuie sa fie mai mare decat 0.")
        self._amount = parsed
        return self

    def in_category(self, category: str) -> "RecurringExpenseBuilder":
        cleaned = category.strip().lower()
        if not cleaned:
            raise ValueError("Categoria este obligatorie.")
        self._category = cleaned
        return self

    def described_as(self, description: str) -> "RecurringExpenseBuilder":
        self._description = description.strip() or "Cheltuiala recurenta"
        return self

    def due_on_day(self, day_of_month: str | int) -> "RecurringExpenseBuilder":
        parsed = int(day_of_month)
        if parsed < 1 or parsed > 31:
            raise ValueError("Ziua recurentei trebuie sa fie intre 1 si 31.")
        self._day_of_month = parsed
        return self

    def build(self) -> RecurringExpense:
        if None in (self._amount, self._category, self._description, self._day_of_month):
            raise ValueError("Cheltuiala recurenta nu este completa.")
        return RecurringExpense(
            id=str(uuid4()),
            amount=self._amount or 0.0,
            category=self._category or "",
            description=self._description or "",
            day_of_month=self._day_of_month or 1,
            active=True,
            created_at=datetime.now(),
        )


class NoteBuilder:
    """Builder: creates validated study notes."""

    def __init__(self) -> None:
        self._title: str | None = None
        self._body: str | None = None
        self._tag: str = "general"

    def titled(self, title: str) -> "NoteBuilder":
        cleaned = title.strip()
        if len(cleaned) < 2:
            raise ValueError("Titlul notitei trebuie sa aiba minim 2 caractere.")
        self._title = cleaned
        return self

    def with_body(self, body: str) -> "NoteBuilder":
        cleaned = body.strip()
        if len(cleaned) < 3:
            raise ValueError("Textul notitei trebuie sa aiba minim 3 caractere.")
        self._body = cleaned
        return self

    def tagged(self, tag: str) -> "NoteBuilder":
        cleaned = tag.strip().lower() or "general"
        self._tag = cleaned
        return self

    def build(self) -> Note:
        if self._title is None or self._body is None:
            raise ValueError("Notita nu este completa.")
        return Note(
            id=str(uuid4()),
            title=self._title,
            body=self._body,
            tag=self._tag,
            created_at=datetime.now(),
        )


class HabitBuilder:
    """Builder: creates validated habits."""

    def __init__(self) -> None:
        self._name: str | None = None

    def named(self, name: str) -> "HabitBuilder":
        cleaned = name.strip()
        if len(cleaned) < 2:
            raise ValueError("Numele obiceiului trebuie sa aiba minim 2 caractere.")
        self._name = cleaned
        return self

    def build(self) -> Habit:
        if self._name is None:
            raise ValueError("Numele obiceiului este obligatoriu.")
        return Habit(
            id=str(uuid4()),
            name=self._name,
            log_dates=[],
            created_at=datetime.now(),
        )
