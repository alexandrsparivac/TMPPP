import re

with open("student_life_helper/conversations.py", "r") as f:
    content = f.read()

new_strategies = """class AddHabitStrategy(ConversationStrategy):
    command_name = "addhabit"
    stages = ["Numele noului obicei (ex: Citește 10 pagini):"]

    def finish(self, user_id: str, answers: dict[str, str]) -> CommandResponse:
        from .adapters import PRODUCTIVITY_KEYBOARD
        name = answers[self.stages[0]]
        self.facade.add_habit(user_id, name)
        return CommandResponse(text=f"✅ Obiceiul '{name}' a fost adăugat!", keyboard=PRODUCTIVITY_KEYBOARD)

class LogHabitStrategy(ConversationStrategy):
    command_name = "loghabit"
    stages = ["Scrie primele litere din ID-ul sau numele obiceiului pentru a-l bifa azi:"]

    def finish(self, user_id: str, answers: dict[str, str]) -> CommandResponse:
        from .adapters import PRODUCTIVITY_KEYBOARD
        prefix = answers[self.stages[0]]
        try:
            habit = self.facade.log_habit(user_id, prefix)
            return CommandResponse(text=f"✅ Ai bifat '{habit.name}' pentru azi. Tine-o tot asa!", keyboard=PRODUCTIVITY_KEYBOARD)
        except Exception as e:
            return CommandResponse(text=f"❌ Nu am putut bifa obiceiul: {e}", keyboard=PRODUCTIVITY_KEYBOARD)

"""

# Register in ConversationManager
content = content.replace("            SetProfileStrategy(self.facade),", "            SetProfileStrategy(self.facade),\n            AddHabitStrategy(self.facade),\n            LogHabitStrategy(self.facade),")

with open("student_life_helper/conversations.py", "w") as f:
    f.write(content + "\n\n" + new_strategies)
