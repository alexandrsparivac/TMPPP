from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import Any, Protocol

from .budget_analytics import BudgetAnalyticsService
from .models import BudgetTransaction, Task
from .storage import StudentStorage


class EventType(str, Enum):
    TASK_ADDED = "task_added"
    TASK_COMPLETED = "task_completed"
    BUDGET_ADDED = "budget_added"


@dataclass(frozen=True)
class DomainEvent:
    event_type: EventType
    user_id: str
    payload: dict[str, Any]


class EventObserver(Protocol):
    """Observer: each observer reacts to domain events independently."""

    def update(self, event: DomainEvent) -> str | None:
        ...


class EventBus:
    """Publisher that notifies observers and collects their messages."""

    def __init__(self) -> None:
        self._observers: dict[EventType, list[EventObserver]] = {}

    def subscribe(self, event_type: EventType, observer: EventObserver) -> None:
        self._observers.setdefault(event_type, []).append(observer)

    def publish(self, event: DomainEvent) -> list[str]:
        messages: list[str] = []
        for observer in self._observers.get(event.event_type, []):
            message = observer.update(event)
            if message:
                messages.append(message)
        return messages


class ReminderObserver:
    """Warns students immediately when a task is close to its deadline."""

    def update(self, event: DomainEvent) -> str | None:
        task = event.payload.get("task")
        if not isinstance(task, Task):
            return None
        today = date.today()
        if task.due_date == today:
            return "Reminder: taskul este pentru azi. Pune-l primul in lista."
        if task.due_date == today + timedelta(days=1):
            return "Reminder: taskul este pentru maine. Planifica macar 30 de minute azi."
        return None


class AchievementObserver:
    """Congratulates the student when all active tasks are done."""

    def __init__(self, storage: StudentStorage) -> None:
        self._storage = storage

    def update(self, event: DomainEvent) -> str | None:
        if event.event_type != EventType.TASK_COMPLETED:
            return None
        remaining = [task for task in self._storage.list_tasks(event.user_id) if not task.completed]
        if not remaining:
            return "Bravo! Nu mai ai taskuri active in lista."
        return f"Progres bun: mai ai {len(remaining)} taskuri active."


class BudgetLimitObserver:
    """Flags a possible budget problem after a new transaction."""

    def __init__(self, storage: StudentStorage) -> None:
        self._storage = storage
        self._analytics = BudgetAnalyticsService()

    def update(self, event: DomainEvent) -> str | None:
        transaction = event.payload.get("transaction")
        if not isinstance(transaction, BudgetTransaction):
            return None
        report = self._analytics.build_report(
            self._storage.list_transactions(event.user_id),
            self._storage.list_budget_limits(event.user_id),
            self._storage.list_recurring_expenses(event.user_id),
        )
        income = float(report["income"])
        expenses = float(report["expenses"])
        limit_statuses = list(report["limits"])
        for status in limit_statuses:
            if str(status["category"]).lower() != transaction.category.lower():
                continue
            percent = float(status["percent"])
            if percent >= 100:
                return f"Buget: categoria {status['category']} a depasit limita lunara."
            if percent >= 80:
                return f"Buget: categoria {status['category']} a folosit peste 80% din limita lunara."
        if income == 0 and expenses > 0:
            return "Buget: ai cheltuieli, dar niciun venit introdus. Adauga venitul lunar pentru analiza."
        if income > 0 and expenses > income:
            return "Buget: cheltuielile au depasit veniturile. Merita revazute mesele, transportul si abonamentele."
        if income > 0 and expenses >= income * 0.8:
            return "Buget: ai folosit peste 80% din venituri. Incearca sa amani cheltuielile neurgente."
        return None


def build_default_event_bus(storage: StudentStorage) -> EventBus:
    bus = EventBus()
    bus.subscribe(EventType.TASK_ADDED, ReminderObserver())
    bus.subscribe(EventType.TASK_COMPLETED, AchievementObserver(storage))
    bus.subscribe(EventType.BUDGET_ADDED, BudgetLimitObserver(storage))
    return bus
