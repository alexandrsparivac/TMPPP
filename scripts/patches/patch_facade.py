import re

with open("student_life_helper/facade.py", "r") as f:
    content = f.read()

# Add Habit to imports
content = content.replace("BudgetTransaction, Note, ScheduleEvent, Task", "BudgetTransaction, Habit, Note, ScheduleEvent, Task")

habit_methods = """
    def add_note(self, user_id: str, title: str, body: str, tag: str) -> None:
        note = Note(str(uuid.uuid4()), title, body, tag, datetime.now())
        self.storage.add_note(user_id, note)

    def list_habits(self, user_id: str) -> list[Habit]:
        return self.storage.list_habits(user_id)

    def add_habit(self, user_id: str, name: str) -> None:
        habit = Habit(str(uuid.uuid4()), name, [], datetime.now())
        self.storage.add_habit(user_id, habit)

    def log_habit(self, user_id: str, habit_prefix: str) -> Habit:
        return self.storage.log_habit(user_id, habit_prefix)
"""

content = content.replace("""    def add_note(self, user_id: str, title: str, body: str, tag: str) -> None:
        note = Note(str(uuid.uuid4()), title, body, tag, datetime.now())
        self.storage.add_note(user_id, note)""", habit_methods)

with open("student_life_helper/facade.py", "w") as f:
    f.write(content)
