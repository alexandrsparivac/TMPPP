import re

with open("student_life_helper/commands.py", "r") as f:
    content = f.read()

new_commands = """class MenuProductivityCommand(BotCommand):
    name = "menuproductivity"
    def execute(self, request: CommandRequest) -> CommandResponse:
        from .adapters import PRODUCTIVITY_KEYBOARD
        return CommandResponse(
            text="⚡️ Meniu Productivitate\\n\\nAici poți porni un Pomodoro sau să îți gestionezi obiceiurile zilnice.",
            keyboard=PRODUCTIVITY_KEYBOARD
        )

class StartPomodoroCommand(BotCommand):
    name = "pomodorostart"
    def execute(self, request: CommandRequest) -> CommandResponse:
        from .ports import ScheduledCommand
        # Set a 25 minutes delay (25 * 60) for real usage, 
        # but let's use a 5-second test or 25 minutes depending on need. 
        # The assignment calls for 25 minutes, we'll configure 25 * 60
        return CommandResponse(
            text="🍅 *Timer Pomodoro pornit!* Ai la dispozitie 25 de minute pentru o sesiune de focus intens. Spor!",
            parse_mode="HTML",
            scheduled_action=ScheduledCommand(delay_seconds=25*60, command_name="pomodorodone")
        )

class PomodoroDoneCommand(BotCommand):
    name = "pomodorodone"
    def execute(self, request: CommandRequest) -> CommandResponse:
        return CommandResponse(
            text="⏰ *Timpul a expirat!* Au trecut cele 25 de minute.\\nIa o pauză de 5 minute și relaxează-te! 🧘‍♂️",
            parse_mode="HTML"
        )

class HabitsCommand(BotCommand):
    name = "habits"
    def __init__(self, facade):
        self.facade = facade
    def execute(self, request: CommandRequest) -> CommandResponse:
        habits = self.facade.list_habits(request.user_id)
        if not habits:
            return CommandResponse(text="Nu ai niciun obicei adaugat momentan.\\nFoloseste butonul '➕ Adauga Obicei'.")
        
        lines = ["📅 *Obiceiurile tale:*\\n"]
        for h in habits:
            freq = len(h.log_dates)
            lines.append(f"• <b>{h.name}</b> (Completat de {freq} ori) [ID: {h.short_id}]")
            
        return CommandResponse(text="\\n".join(lines), parse_mode="HTML")

class LogHabitCommand(BotCommand):
    name = "loghabit"
    def __init__(self, facade):
        self.facade = facade
    def execute(self, request: CommandRequest) -> CommandResponse:
        try:
            habit = self.facade.log_habit(request.user_id, request.args.strip())
            return CommandResponse(text=f"✅ Obiceiul '{habit.name}' a fost bifat pentru astazi!")
        except Exception as e:
            return CommandResponse(text=f"❌ Eroare: {e}")
"""

with open("student_life_helper/commands.py", "w") as f:
    f.write(content + "\n\n" + new_commands)
