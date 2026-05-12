from __future__ import annotations

from .builders import (
    BudgetCategoryLimitBuilder,
    BudgetTransactionBuilder,
    HabitBuilder,
    NoteBuilder,
    RecurringExpenseBuilder,
    ScheduleEventBuilder,
    StudentProfileBuilder,
    TaskBuilder,
)
from .budget_analytics import BudgetAnalyticsService
from .events import DomainEvent, EventBus, EventType
from .models import (
    BudgetCategoryLimit,
    BudgetTransaction,
    Habit,
    Note,
    RecurringExpense,
    ScheduleEvent,
    StudentProfile,
    Task,
    TransactionType,
)
from .storage import StudentStorage
from .strategies import TaskSortStrategyFactory, TipStrategyFactory
from .study_planner import SmartStudyPlanner


class StudentLifeFacade:
    """Facade: commands use this API instead of touching storage and services."""

    def __init__(
        self,
        storage: StudentStorage,
        event_bus: EventBus,
        budget_analytics: BudgetAnalyticsService | None = None,
        study_planner: SmartStudyPlanner | None = None,
    ) -> None:
        self._storage = storage
        self._event_bus = event_bus
        self._budget_analytics = budget_analytics or BudgetAnalyticsService()
        self._study_planner = study_planner or SmartStudyPlanner()

    def create_profile(
        self,
        user_id: str,
        name: str,
        university: str,
        faculty: str,
        group: str,
        year: str,
    ) -> StudentProfile:
        profile = (
            StudentProfileBuilder()
            .named(name)
            .at_university(university)
            .in_faculty(faculty)
            .in_group(group)
            .in_year(year)
            .build()
        )
        self._storage.set_profile(user_id, profile)
        return profile

    def get_all_users(self) -> list[str]:
        return self._storage.get_all_users()

    def get_profile(self, user_id: str) -> StudentProfile | None:
        return self._storage.get_profile(user_id)

    def add_task(self, user_id: str, title: str, due_date: str, priority: str) -> tuple[Task, list[str]]:
        task = TaskBuilder().titled(title).due_on(due_date).with_priority(priority).build()
        self._storage.add_task(user_id, task)
        notes = self._event_bus.publish(
            DomainEvent(EventType.TASK_ADDED, user_id=user_id, payload={"task": task})
        )
        return task, notes

    def list_tasks(self, user_id: str) -> tuple[list[Task], str]:
        all_tasks = self._storage.list_tasks(user_id)
        active_tasks = [t for t in all_tasks if not t.completed]
        strategy_name = self._storage.get_task_strategy(user_id)
        strategy = TaskSortStrategyFactory.create(strategy_name)
        return strategy.sort(active_tasks), strategy.name

    def list_deadlines(self, user_id: str) -> list[Task]:
        tasks = [task for task in self._storage.list_tasks(user_id) if not task.completed]
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda task: (task.due_date, priority_order[task.priority.value]))

    def complete_task(self, user_id: str, task_selector: str) -> tuple[Task, list[str]]:
        selector = task_selector.strip()
        task_id = self._resolve_task_selector(user_id, selector)
        task = self._storage.complete_task(user_id, task_id)
        notes = self._event_bus.publish(
            DomainEvent(EventType.TASK_COMPLETED, user_id=user_id, payload={"task": task})
        )
        return task, notes

    def _resolve_task_selector(self, user_id: str, selector: str) -> str:
        tasks, _strategy = self.list_tasks(user_id)
        active_tasks = [task for task in tasks if not task.completed]
        if selector.isdigit():
            index = int(selector)
            if index < 1 or index > len(active_tasks):
                raise ValueError("Nu exista task activ cu acest numar.")
            return active_tasks[index - 1].id

        exact_title_matches = [
            task for task in active_tasks if task.title.strip().lower() == selector.lower()
        ]
        if len(exact_title_matches) == 1:
            return exact_title_matches[0].id
        if len(exact_title_matches) > 1:
            raise ValueError("Exista mai multe taskuri cu aceasta denumire. Foloseste numarul din /tasks.")

        return selector

    def set_task_strategy(self, user_id: str, strategy_name: str) -> str:
        strategy = TaskSortStrategyFactory.create(strategy_name)
        self._storage.set_task_strategy(user_id, strategy.name)
        return strategy.name

    def available_task_strategies(self) -> list[str]:
        return TaskSortStrategyFactory.names()

    def add_schedule_event(
        self,
        user_id: str,
        weekday: str,
        time_value: str,
        subject: str,
        location: str,
    ) -> ScheduleEvent:
        event = (
            ScheduleEventBuilder()
            .on_weekday(weekday)
            .at_time(time_value)
            .for_subject(subject)
            .in_location(location)
            .build()
        )
        self._storage.add_schedule_event(user_id, event)
        return event

    def list_schedule(self, user_id: str) -> list[ScheduleEvent]:
        events = self._storage.list_schedule(user_id)
        day_order = {
            "Luni": 0,
            "Marti": 1,
            "Miercuri": 2,
            "Joi": 3,
            "Vineri": 4,
            "Sambata": 5,
            "Duminica": 6,
        }
        return sorted(events, key=lambda item: (day_order.get(item.weekday, 99), item.time))

    def add_transaction(
        self,
        user_id: str,
        kind: str,
        amount: str,
        category: str,
        description: str,
    ) -> tuple[BudgetTransaction, list[str]]:
        transaction = (
            BudgetTransactionBuilder()
            .of_type(kind)
            .with_amount(amount)
            .in_category(category)
            .described_as(description)
            .build()
        )
        self._storage.add_transaction(user_id, transaction)
        notes = self._event_bus.publish(
            DomainEvent(EventType.BUDGET_ADDED, user_id=user_id, payload={"transaction": transaction})
        )
        return transaction, notes

    def budget_summary(self, user_id: str) -> dict[str, float]:
        transactions = self._storage.list_transactions(user_id)
        income = sum(item.amount for item in transactions if item.kind == TransactionType.INCOME)
        expenses = sum(item.amount for item in transactions if item.kind == TransactionType.EXPENSE)
        return {
            "income": income,
            "expenses": expenses,
            "balance": income - expenses,
        }

    def set_budget_limit(self, user_id: str, category: str, amount: str) -> BudgetCategoryLimit:
        limit = (
            BudgetCategoryLimitBuilder()
            .in_category(category)
            .with_monthly_limit(amount)
            .build()
        )
        self._storage.set_budget_limit(user_id, limit)
        return limit

    def list_budget_limit_statuses(self, user_id: str) -> list[dict[str, float | str]]:
        return list(self.budget_report(user_id)["limits"])

    def add_recurring_expense(
        self,
        user_id: str,
        amount: str,
        category: str,
        description: str,
        day_of_month: str,
    ) -> RecurringExpense:
        expense = (
            RecurringExpenseBuilder()
            .with_amount(amount)
            .in_category(category)
            .described_as(description)
            .due_on_day(day_of_month)
            .build()
        )
        self._storage.add_recurring_expense(user_id, expense)
        return expense

    def list_recurring_expenses(self, user_id: str) -> list[RecurringExpense]:
        return self._storage.list_recurring_expenses(user_id)

    def budget_report(self, user_id: str) -> dict[str, object]:
        return self._budget_analytics.build_report(
            self._storage.list_transactions(user_id),
            self._storage.list_budget_limits(user_id),
            self._storage.list_recurring_expenses(user_id),
        )

    def budget_forecast(self, user_id: str) -> dict[str, object]:
        report = self.budget_report(user_id)
        return {
            "month": report["month"],
            "income": report["income"],
            "expenses": report["expenses"],
            "recurring_remaining": report["recurring_remaining"],
            "projected_expenses": report["projected_expenses"],
            "projected_balance": report["projected_balance"],
            "remaining_days": report["remaining_days"],
            "safe_daily_budget": report["safe_daily_budget"],
            "alerts": report["alerts"],
        }

    def get_tip(self, user_id: str, tip_type: str) -> str:
        strategy = TipStrategyFactory.create(tip_type)
        return strategy.generate(
            self._storage.get_profile(user_id),
            self._storage.list_tasks(user_id),
            self._storage.list_transactions(user_id),
        )

    def available_tip_types(self) -> list[str]:
        return TipStrategyFactory.names()

    def add_note(self, user_id: str, title: str, body: str, tag: str) -> Note:
        note = NoteBuilder().titled(title).with_body(body).tagged(tag).build()
        self._storage.add_note(user_id, note)
        return note

    def list_habits(self, user_id: str) -> list[Habit]:
        return self._storage.list_habits(user_id)

    def add_habit(self, user_id: str, name: str) -> Habit:
        habit = HabitBuilder().named(name).build()
        self._storage.add_habit(user_id, habit)
        return habit

    def log_habit(self, user_id: str, habit_selector: str) -> tuple[Habit, str]:
        selector = habit_selector.strip()
        habit_id = self._resolve_habit_selector(user_id, selector)
        habit = self._storage.log_habit(user_id, habit_id)
        return habit, "done"

    def _resolve_habit_selector(self, user_id: str, selector: str) -> str:
        habits = self.list_habits(user_id)
        if selector.isdigit():
            index = int(selector)
            if index < 1 or index > len(habits):
                raise ValueError("Nu exista obicei cu acest numar.")
            return habits[index - 1].id

        exact_title_matches = [
            h for h in habits if h.name.strip().lower() == selector.lower()
        ]
        if len(exact_title_matches) == 1:
            return exact_title_matches[0].id
        if len(exact_title_matches) > 1:
            raise ValueError("Exista mai multe obiceiuri cu aceasta denumire. Foloseste numarul din /habits.")

        return selector

    def list_notes(self, user_id: str) -> list[Note]:
        return sorted(self._storage.list_notes(user_id), key=lambda note: note.created_at, reverse=True)

    def calculate_required_exam_grade(
        self,
        current_grade: str,
        desired_final: str,
        exam_weight_percent: str,
    ) -> dict[str, float | str]:
        current = self._grade_value(current_grade, "Nota curenta")
        desired = self._grade_value(desired_final, "Nota dorita")
        weight = float(str(exam_weight_percent).replace(",", "."))
        if weight <= 0 or weight >= 100:
            raise ValueError("Ponderea examenului trebuie sa fie intre 1 si 99.")
        exam_weight = weight / 100
        required = (desired - current * (1 - exam_weight)) / exam_weight
        status = "ok"
        if required <= 1:
            status = "easy"
        elif required > 10:
            status = "impossible"
        return {
            "current": current,
            "desired": desired,
            "weight_percent": weight,
            "required": required,
            "status": status,
        }

    def generate_study_plan(self, user_id: str) -> list[str]:
        result = self._study_planner.build_weekly_plan(
            self.list_deadlines(user_id),
            self.list_schedule(user_id),
        )
        return result.to_lines()

    def search(self, user_id: str, query: str) -> list[str]:
        normalized = query.strip().lower()
        if not normalized:
            raise ValueError("Scrie ce vrei sa cauti. Exemplu: /search examen")

        results: list[str] = []
        for task in self._storage.list_tasks(user_id):
            haystack = f"{task.title} {task.due_date.isoformat()} {task.priority.value}".lower()
            if normalized in haystack:
                status = "finalizat" if task.completed else "activ"
                results.append(
                    f"Task: {task.title} | {task.due_date.isoformat()} | {task.priority.value} | {status}"
                )

        for event in self._storage.list_schedule(user_id):
            haystack = f"{event.weekday} {event.time} {event.subject} {event.location}".lower()
            if normalized in haystack:
                results.append(
                    f"Orar: {event.weekday} {event.time} | {event.subject} | {event.location}"
                )

        for transaction in self._storage.list_transactions(user_id):
            haystack = f"{transaction.kind.value} {transaction.category} {transaction.description}".lower()
            if normalized in haystack:
                sign = "+" if transaction.kind == TransactionType.INCOME else "-"
                results.append(
                    f"Buget: {sign}{transaction.amount:.2f} | {transaction.category} | {transaction.description}"
                )

        for note in self._storage.list_notes(user_id):
            haystack = f"{note.title} {note.body} {note.tag}".lower()
            if normalized in haystack:
                results.append(f"Notita: {note.title} | #{note.tag} | {note.body}")

        return results

    def _grade_value(self, value: str, label: str) -> float:
        parsed = float(str(value).replace(",", "."))
        if parsed < 1 or parsed > 10:
            raise ValueError(f"{label} trebuie sa fie intre 1 si 10.")
        return parsed
