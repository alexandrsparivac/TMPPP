from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from .models import BudgetTransaction, Priority, StudentProfile, Task, TransactionType


PRIORITY_SCORE = {
    Priority.HIGH: 0,
    Priority.MEDIUM: 1,
    Priority.LOW: 2,
}


class TaskSortStrategy(ABC):
    """Strategy: interchangeable task prioritization algorithm."""

    name: str

    @abstractmethod
    def sort(self, tasks: list[Task]) -> list[Task]:
        raise NotImplementedError


class DeadlineFirstStrategy(TaskSortStrategy):
    name = "deadline"

    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda task: (task.completed, task.due_date, PRIORITY_SCORE[task.priority]))


class PriorityFirstStrategy(TaskSortStrategy):
    name = "priority"

    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda task: (task.completed, PRIORITY_SCORE[task.priority], task.due_date))


class BalancedTaskStrategy(TaskSortStrategy):
    name = "balanced"

    def sort(self, tasks: list[Task]) -> list[Task]:
        today = date.today()

        def score(task: Task) -> tuple[bool, int, int, date]:
            days_left = max((task.due_date - today).days, 0)
            urgency = min(days_left, 14)
            return (task.completed, urgency + PRIORITY_SCORE[task.priority] * 3, PRIORITY_SCORE[task.priority], task.due_date)

        return sorted(tasks, key=score)


class TaskSortStrategyFactory:
    _strategies = {
        DeadlineFirstStrategy.name: DeadlineFirstStrategy,
        PriorityFirstStrategy.name: PriorityFirstStrategy,
        BalancedTaskStrategy.name: BalancedTaskStrategy,
    }

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._strategies)

    @classmethod
    def create(cls, name: str) -> TaskSortStrategy:
        normalized = name.strip().lower()
        if normalized not in cls._strategies:
            raise ValueError("Strategia trebuie sa fie: " + ", ".join(cls.names()))
        return cls._strategies[normalized]()


class TipStrategy(ABC):
    """Strategy: different advice generators for student needs."""

    name: str

    @abstractmethod
    def generate(
        self,
        profile: StudentProfile | None,
        tasks: list[Task],
        transactions: list[BudgetTransaction],
    ) -> str:
        raise NotImplementedError


class StudyTipStrategy(TipStrategy):
    name = "study"

    def generate(
        self,
        profile: StudentProfile | None,
        tasks: list[Task],
        transactions: list[BudgetTransaction],
    ) -> str:
        active = [task for task in tasks if not task.completed]
        high = [task for task in active if task.priority == Priority.HIGH]
        if high:
            return f"Invatare: incepe cu '{high[0].title}' si lucreaza in 2 sesiuni Pomodoro."
        if active:
            return f"Invatare: alege taskul '{active[0].title}' si noteaza primul pas concret."
        return "Invatare: lista este libera. Recapituleaza 20 de minute materia cea mai grea."


class MoneyTipStrategy(TipStrategy):
    name = "money"

    def generate(
        self,
        profile: StudentProfile | None,
        tasks: list[Task],
        transactions: list[BudgetTransaction],
    ) -> str:
        income = sum(item.amount for item in transactions if item.kind == TransactionType.INCOME)
        expenses = sum(item.amount for item in transactions if item.kind == TransactionType.EXPENSE)
        if income == 0:
            return "Bani: adauga venitul lunar, apoi pot calcula soldul si riscul de depasire."
        remaining = income - expenses
        return f"Bani: mai ai {remaining:.2f} disponibili. Tinta buna: pastreaza macar 10% ca rezerva."


class WellnessTipStrategy(TipStrategy):
    name = "wellness"

    def generate(
        self,
        profile: StudentProfile | None,
        tasks: list[Task],
        transactions: list[BudgetTransaction],
    ) -> str:
        active_count = len([task for task in tasks if not task.completed])
        if active_count >= 5:
            return "Wellness: ai multe taskuri active. Blocheaza o pauza reala dupa primele doua."
        return "Wellness: programeaza somnul ca pe un curs. Energia buna scade costul fiecarui task."


class TipStrategyFactory:
    _strategies = {
        StudyTipStrategy.name: StudyTipStrategy,
        MoneyTipStrategy.name: MoneyTipStrategy,
        WellnessTipStrategy.name: WellnessTipStrategy,
    }

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._strategies)

    @classmethod
    def create(cls, name: str) -> TipStrategy:
        normalized = name.strip().lower()
        if normalized not in cls._strategies:
            raise ValueError("Tipul de sfat trebuie sa fie: " + ", ".join(cls.names()))
        return cls._strategies[normalized]()
