from __future__ import annotations

from typing import Any, Protocol

from pymongo import MongoClient

from .models import (
    BudgetCategoryLimit,
    BudgetTransaction,
    Habit,
    Note,
    RecurringExpense,
    ScheduleEvent,
    StudentProfile,
    Task,
)


class StudentStorage(Protocol):
    def get_all_users(self) -> list[str]:
        ...

    def get_profile(self, user_id: str) -> StudentProfile | None:
        ...

    def set_profile(self, user_id: str, profile: StudentProfile) -> None:
        ...

    def list_tasks(self, user_id: str) -> list[Task]:
        ...

    def add_task(self, user_id: str, task: Task) -> None:
        ...

    def complete_task(self, user_id: str, task_prefix: str) -> Task:
        ...

    def set_task_strategy(self, user_id: str, strategy_name: str) -> None:
        ...

    def get_task_strategy(self, user_id: str) -> str:
        ...

    def list_schedule(self, user_id: str) -> list[ScheduleEvent]:
        ...

    def add_schedule_event(self, user_id: str, event: ScheduleEvent) -> None:
        ...

    def list_transactions(self, user_id: str) -> list[BudgetTransaction]:
        ...

    def add_transaction(self, user_id: str, transaction: BudgetTransaction) -> None:
        ...

    def list_budget_limits(self, user_id: str) -> list[BudgetCategoryLimit]:
        ...

    def set_budget_limit(self, user_id: str, limit: BudgetCategoryLimit) -> None:
        ...

    def list_recurring_expenses(self, user_id: str) -> list[RecurringExpense]:
        ...

    def add_recurring_expense(self, user_id: str, expense: RecurringExpense) -> None:
        ...

    def list_notes(self, user_id: str) -> list[Note]:
        ...

    def add_note(self, user_id: str, note: Note) -> None:
        ...

    def list_habits(self, user_id: str) -> list[Habit]:
        ...

    def add_habit(self, user_id: str, habit: Habit) -> None:
        ...

    def log_habit(self, user_id: str, habit_prefix: str) -> Habit:
        ...


class MongoStorage:
    """MongoDB repository used by the bot features."""

    def __init__(
        self,
        mongo_uri: str = "mongodb://localhost:27017",
        database: str = "student_life_helper",
        collection: str = "users",
        default_strategy: str = "deadline",
        client: Any | None = None,
    ) -> None:
        self.default_strategy = default_strategy
        self._client = client or MongoClient(mongo_uri)
        self._collection = self._client[database][collection]

    def get_all_users(self) -> list[str]:
        return [str(item["_id"]) for item in self._collection.find({}, {"_id": 1})]

    def get_profile(self, user_id: str) -> StudentProfile | None:
        return StudentProfile.from_dict(self._get_user(user_id).get("profile"))

    def set_profile(self, user_id: str, profile: StudentProfile) -> None:
        self._ensure_user(user_id)
        self._collection.update_one(
            {"_id": str(user_id)},
            {"$set": {"profile": profile.to_dict()}},
        )

    def list_tasks(self, user_id: str) -> list[Task]:
        return [Task.from_dict(item) for item in self._get_user(user_id).get("tasks", [])]

    def add_task(self, user_id: str, task: Task) -> None:
        self._push(user_id, "tasks", task.to_dict())

    def complete_task(self, user_id: str, task_prefix: str) -> Task:
        user = self._ensure_user(user_id)
        tasks = [Task.from_dict(item) for item in user.get("tasks", [])]
        matches = [task for task in tasks if task.id.startswith(task_prefix)]
        if not matches:
            raise ValueError("Nu am gasit un task cu acest id.")
        if len(matches) > 1:
            raise ValueError("Id-ul este ambiguu. Scrie mai multe caractere din id.")
        completed = matches[0].mark_completed()
        user["tasks"] = [
            (completed if task.id == completed.id else task).to_dict()
            for task in tasks
        ]
        self._replace_user(user)
        return completed

    def set_task_strategy(self, user_id: str, strategy_name: str) -> None:
        self._ensure_user(user_id)
        self._collection.update_one(
            {"_id": str(user_id)},
            {"$set": {"preferences.task_strategy": strategy_name}},
        )

    def get_task_strategy(self, user_id: str) -> str:
        return str(
            self._get_user(user_id)
            .get("preferences", {})
            .get("task_strategy", self.default_strategy)
        )

    def list_schedule(self, user_id: str) -> list[ScheduleEvent]:
        return [
            ScheduleEvent.from_dict(item)
            for item in self._get_user(user_id).get("schedule", [])
        ]

    def add_schedule_event(self, user_id: str, event: ScheduleEvent) -> None:
        self._push(user_id, "schedule", event.to_dict())

    def list_transactions(self, user_id: str) -> list[BudgetTransaction]:
        return [
            BudgetTransaction.from_dict(item)
            for item in self._get_user(user_id).get("transactions", [])
        ]

    def add_transaction(self, user_id: str, transaction: BudgetTransaction) -> None:
        self._push(user_id, "transactions", transaction.to_dict())

    def list_budget_limits(self, user_id: str) -> list[BudgetCategoryLimit]:
        return [
            BudgetCategoryLimit.from_dict(item)
            for item in self._get_user(user_id).get("budget_limits", [])
        ]

    def set_budget_limit(self, user_id: str, limit: BudgetCategoryLimit) -> None:
        user = self._ensure_user(user_id)
        limits = [
            BudgetCategoryLimit.from_dict(item)
            for item in user.get("budget_limits", [])
        ]
        user["budget_limits"] = [
            item.to_dict()
            for item in limits
            if item.category.lower() != limit.category.lower()
        ]
        user["budget_limits"].append(limit.to_dict())
        self._replace_user(user)

    def list_recurring_expenses(self, user_id: str) -> list[RecurringExpense]:
        return [
            RecurringExpense.from_dict(item)
            for item in self._get_user(user_id).get("recurring_expenses", [])
        ]

    def add_recurring_expense(self, user_id: str, expense: RecurringExpense) -> None:
        self._push(user_id, "recurring_expenses", expense.to_dict())

    def list_notes(self, user_id: str) -> list[Note]:
        return [Note.from_dict(item) for item in self._get_user(user_id).get("notes", [])]

    def add_note(self, user_id: str, note: Note) -> None:
        self._push(user_id, "notes", note.to_dict())

    def list_habits(self, user_id: str) -> list[Habit]:
        return [Habit.from_dict(item) for item in self._get_user(user_id).get("habits", [])]

    def add_habit(self, user_id: str, habit: Habit) -> None:
        self._push(user_id, "habits", habit.to_dict())

    def log_habit(self, user_id: str, habit_prefix: str) -> Habit:
        user = self._ensure_user(user_id)
        habits = [Habit.from_dict(item) for item in user.get("habits", [])]
        matches = [habit for habit in habits if habit.id.startswith(habit_prefix)]
        if not matches:
            raise ValueError("Nu am gasit un habit cu acest id.")
        if len(matches) > 1:
            raise ValueError("Id-ul este ambiguu.")
        logged = matches[0].log_today()
        user["habits"] = [
            (logged if habit.id == logged.id else habit).to_dict()
            for habit in habits
        ]
        self._replace_user(user)
        return logged

    def _push(self, user_id: str, field: str, item: dict[str, Any]) -> None:
        self._ensure_user(user_id)
        self._collection.update_one(
            {"_id": str(user_id)},
            {"$push": {field: item}},
        )

    def _get_user(self, user_id: str) -> dict[str, Any]:
        document = self._collection.find_one({"_id": str(user_id)})
        if document is None:
            return self._empty_user(str(user_id))
        normalized = self._normalize_user(document, str(user_id))
        if normalized != document:
            self._replace_user(normalized)
        return normalized

    def _ensure_user(self, user_id: str) -> dict[str, Any]:
        normalized_id = str(user_id)
        self._collection.update_one(
            {"_id": normalized_id},
            {"$setOnInsert": self._empty_user_fields()},
            upsert=True,
        )
        return self._get_user(normalized_id)

    def _replace_user(self, user: dict[str, Any]) -> None:
        self._collection.replace_one({"_id": user["_id"]}, user, upsert=True)

    def _empty_user(self, user_id: str) -> dict[str, Any]:
        return {"_id": str(user_id), **self._empty_user_fields()}

    def _empty_user_fields(self) -> dict[str, Any]:
        return {
            "profile": None,
            "tasks": [],
            "schedule": [],
            "transactions": [],
            "budget_limits": [],
            "recurring_expenses": [],
            "notes": [],
            "habits": [],
            "preferences": {"task_strategy": self.default_strategy},
        }

    def _normalize_user(self, user: dict[str, Any], user_id: str) -> dict[str, Any]:
        normalized = self._empty_user(user_id)
        normalized.update(user)
        normalized["preferences"] = {
            **self._empty_user_fields()["preferences"],
            **dict(user.get("preferences", {})),
        }
        return normalized
