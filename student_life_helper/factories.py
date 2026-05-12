from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from . import commands_productivity as prod_cmds
from .command_base import BotCommand
from .commands import (
    AddScheduleCommand,
    AddNoteCommand,
    AddTaskCommand,
    BudgetCommand,
    BudgetForecastCommand,
    BudgetLimitCommand,
    BudgetLimitsCommand,
    BudgetReportCommand,
    DeadlinesCommand,
    DoneCommand,
    GradeCalcCommand,
    HelpCommand,
    NotesCommand,
    ProfileCommand,
    RecurringExpenseCommand,
    RecurringExpensesCommand,
    ScheduleCommand,
    SearchCommand,
    StartCommand,
    MenuTasksCommand,
    MenuScheduleCommand,
    MenuStudyCommand,
    MenuFinanceCommand,
    MenuTipsCommand,
    SettingsCommand,
    StrategyCommand,
    StudyPlanCommand,
    TasksCommand,
    TipCommand,
    UnknownCommand,
)
from .commands_ai import ExplainCommand
from .decorators import ErrorHandlingCommandDecorator, LoggingCommandDecorator
from .facade import StudentLifeFacade
from .ui import example, h, title as ui_title


class BaseCommandFactory(ABC):
    """Factory Method: subclasses decide which concrete command is created."""

    def get_command(self, name: str) -> BotCommand:
        command = self.create_command(name)
        return self.decorate(command)

    @abstractmethod
    def create_command(self, name: str) -> BotCommand:
        raise NotImplementedError

    def decorate(self, command: BotCommand) -> BotCommand:
        return ErrorHandlingCommandDecorator(LoggingCommandDecorator(command))


class StudentCommandFactory(BaseCommandFactory):
    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade
        self._creators: dict[str, Callable[[], BotCommand]] = {
            "start": StartCommand,
            "help": lambda: HelpCommand(self.help_text),
            "profile": lambda: ProfileCommand(self._facade),
            "addtask": lambda: AddTaskCommand(self._facade),
            "tasks": lambda: TasksCommand(self._facade),
            "done": lambda: DoneCommand(self._facade),
            "strategy": lambda: StrategyCommand(self._facade),
            "deadlines": lambda: DeadlinesCommand(self._facade),
            "search": lambda: SearchCommand(self._facade),
            "addnote": lambda: AddNoteCommand(self._facade),
            "notes": lambda: NotesCommand(self._facade),
            "studyplan": lambda: StudyPlanCommand(self._facade),
            "gradecalc": lambda: GradeCalcCommand(self._facade),
            "addschedule": lambda: AddScheduleCommand(self._facade),
            "schedule": lambda: ScheduleCommand(self._facade),
            "budget": lambda: BudgetCommand(self._facade),
            "budgetlimit": lambda: BudgetLimitCommand(self._facade),
            "budgetlimits": lambda: BudgetLimitsCommand(self._facade),
            "recurringexpense": lambda: RecurringExpenseCommand(self._facade),
            "recurringexpenses": lambda: RecurringExpensesCommand(self._facade),
            "budgetforecast": lambda: BudgetForecastCommand(self._facade),
            "budgetreport": lambda: BudgetReportCommand(self._facade),
            "tip": lambda: TipCommand(self._facade),
            "addhabit": lambda: prod_cmds.AddHabitCommand(self._facade),
            "menuproductivity": lambda: prod_cmds.MenuProductivityCommand(),
            "menuhabits": lambda: prod_cmds.MenuHabitsCommand(),
            "explain": lambda: ExplainCommand(),
            "pomodorostart": lambda: prod_cmds.StartPomodoroCommand(),
            "pomodorodone": lambda: prod_cmds.PomodoroDoneCommand(),
            "habits": lambda: prod_cmds.HabitsCommand(self._facade),
            "loghabit": lambda: prod_cmds.LogHabitCommand(self._facade),

            "menutasks": MenuTasksCommand,
            "menuschedule": MenuScheduleCommand,
            "menustudy": MenuStudyCommand,
            "menufinance": MenuFinanceCommand,
            "menutips": MenuTipsCommand,
            "settings": SettingsCommand,
        }
        self._aliases = {
            "taskuri": "tasks",
            "deadline": "deadlines",
            "termene": "deadlines",
            "cauta": "search",
            "notite": "notes",
            "notita": "addnote",
            "plan": "studyplan",
            "note": "gradecalc",
            "nota": "gradecalc",
            "orar": "schedule",
            "program": "schedule",
            "sfat": "tip",
            "buget": "budget",
            "limitebuget": "budgetlimits",
            "predictiebuget": "budgetforecast",
            "raportbuget": "budgetreport",
            "recurente": "recurringexpenses",
            "setari": "settings",
            "productivitate": "menuproductivity",
        }
        self._help_order = [
            StartCommand,
            HelpCommand,
            MenuTasksCommand,
            MenuScheduleCommand,
            MenuStudyCommand,
            MenuFinanceCommand,
            MenuTipsCommand,
            SettingsCommand,
            ProfileCommand,
            AddTaskCommand,
            TasksCommand,
            DoneCommand,
            StrategyCommand,
            DeadlinesCommand,
            SearchCommand,
            AddNoteCommand,
            NotesCommand,
            StudyPlanCommand,
            GradeCalcCommand,
            AddScheduleCommand,
            ScheduleCommand,
            BudgetCommand,
            BudgetLimitCommand,
            BudgetLimitsCommand,
            RecurringExpenseCommand,
            RecurringExpensesCommand,
            BudgetForecastCommand,
            BudgetReportCommand,
            TipCommand,
        ]

    def create_command(self, name: str) -> BotCommand:
        normalized = name.strip().lower().lstrip("/")
        normalized = self._aliases.get(normalized, normalized)
        creator = self._creators.get(normalized)
        if creator is None:
            return UnknownCommand()
        return creator()

    def help_text(self) -> str:
        lines = [f"{ui_title('❓', 'Comenzi Student Life Helper')}"]
        for command_type in self._help_order:
            lines.append(f"• {example(command_type.usage)}\n  {h(command_type.description)}")
        return "\n\n".join(lines)
