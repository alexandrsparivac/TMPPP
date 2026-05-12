import re

with open("student_life_helper/storage.py", "r") as f:
    content = f.read()

# Make sure we import Habit
content = content.replace("from .models import BudgetTransaction, Note, ScheduleEvent, StudentProfile, Task", "from .models import BudgetTransaction, Habit, Note, ScheduleEvent, StudentProfile, Task")

habit_methods = """
    def list_habits(self, user_id: str) -> list[Habit]:
        return [Habit.from_dict(item) for item in self._get_user(user_id).get("habits", [])]

    def add_habit(self, user_id: str, habit: Habit) -> None:
        data = self._read()
        user = self._ensure_user(data, user_id)
        user.setdefault("habits", []).append(habit.to_dict())
        self._write(data)

    def log_habit(self, user_id: str, habit_prefix: str) -> Habit:
        data = self._read()
        user = self._ensure_user(data, user_id)
        habits = [Habit.from_dict(item) for item in user.get("habits", [])]
        matches = [h for h in habits if h.id.startswith(habit_prefix)]
        if not matches:
            raise ValueError("Nu am gasit un habit cu acest id.")
        if len(matches) > 1:
            raise ValueError("Id-ul este ambiguu.")
        logged = matches[0].log_today()
        user["habits"] = [
            (logged if task.id == logged.id else task).to_dict()
            for task in habits
        ]
        self._write(data)
        return logged

    def _get_user(self, user_id: str) -> dict[str, Any]:
"""

content = content.replace("    def _get_user(self, user_id: str) -> dict[str, Any]:", habit_methods)

content = content.replace('"notes": [],', '"notes": [], "habits": [],')

with open("student_life_helper/storage.py", "w") as f:
    f.write(content)
