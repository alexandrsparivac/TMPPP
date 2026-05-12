from __future__ import annotations

from .command_base import BotCommand
from .ports import CommandRequest, CommandResponse, ScheduledCommand
from .facade import StudentLifeFacade


class MenuProductivityCommand(BotCommand):
    name = "menuproductivity"
    description = "Deschide submeniul pentru productivitate."
    usage = "/menuproductivity"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from .adapters import PRODUCTIVITY_KEYBOARD
        return CommandResponse(
            text="⚡️ Meniu Productivitate\n\nAici poti porni un Pomodoro sau sa gestionezi obiceiurile zilnice.",
            keyboard=PRODUCTIVITY_KEYBOARD,
        )


class MenuHabitsCommand(BotCommand):
    name = "menuhabits"
    description = "Deschide submeniul pentru obiceiuri."
    usage = "/menuhabits"
    
    def execute(self, request: CommandRequest) -> CommandResponse:
        from .adapters import HABITS_KEYBOARD
        return CommandResponse(
            text="📅 Meniu Obiceiuri\n\nAici îți poți vizualiza, crea și bifa obiceiurile zilnice.",
            keyboard=HABITS_KEYBOARD
        )

class StartPomodoroCommand(BotCommand):
    name = "pomodorostart"
    description = "Porneste o sesiune Pomodoro."
    usage = "/pomodorostart minute"
    
    def execute(self, request: CommandRequest) -> CommandResponse:
        try:
            minutes = int(request.args.strip()) if request.args.strip() else 25
        except ValueError:
            minutes = 25
        return CommandResponse(
            text=f"🍅 Timer Pomodoro pornit! Sesiune de {minutes} de minute. Spor la învățat!",
            scheduled_action=ScheduledCommand(delay_seconds=minutes*60, command_name="pomodorodone")
        )

class PomodoroDoneCommand(BotCommand):
    name = "pomodorodone"
    description = "Anunta finalizarea sesiunii Pomodoro."
    usage = "/pomodorodone"
    
    def execute(self, request: CommandRequest) -> CommandResponse:
        return CommandResponse(
            text="⏰ Timpul a expirat! A venit momentul pentru o scurta pauza de 5 minute.\nPentru a incepe din nou, foloseste 🍅 Start Pomodoro."
        )

class HabitsCommand(BotCommand):
    name = "habits"
    description = "Listeaza obiceiurile salvate."
    usage = "/habits"
    
    def __init__(self, facade: StudentLifeFacade) -> None:
        self.facade = facade
        
    def execute(self, request: CommandRequest) -> CommandResponse:
        habits = self.facade.list_habits(request.user_id)
        if not habits:
            return CommandResponse(text="Nu ai niciun obicei adaugat momentan.\nFoloseste comanda pentru a adauga unul nou.")
        
        lines = ["📅 Obiceiurile tale:"]
        for habit in habits:
            freq = len(habit.log_dates)
            lines.append(f"• {habit.name} - (Completat de {freq} ori)")
            
        return CommandResponse(text="\n".join(lines))

class AddHabitCommand(BotCommand):
    name = "addhabit"
    description = "Adauga un obicei zilnic."
    usage = "/addhabit nume"
    
    def __init__(self, facade: StudentLifeFacade) -> None:
        self.facade = facade
        
    def execute(self, request: CommandRequest) -> CommandResponse:
        try:
            self.facade.add_habit(request.user_id, request.args)
            return CommandResponse(text=f"Obiceiul '{request.args}' a fost adaugat cu succes! ")
        except ValueError as err:
            return CommandResponse(text=str(err))

class LogHabitCommand(BotCommand):
    name = "loghabit"
    description = "Bifeaza un obicei pentru ziua curenta."
    usage = "/loghabit numar_sau_nume"
    
    def __init__(self, facade: StudentLifeFacade) -> None:
        self.facade = facade
        
    def execute(self, request: CommandRequest) -> CommandResponse:
        try:
            habit, _ = self.facade.log_habit(request.user_id, request.args)
            return CommandResponse(text=f"✅ Ai bifat obiceiul: {habit.name}!")
        except ValueError as err:
            return CommandResponse(text=str(err))
