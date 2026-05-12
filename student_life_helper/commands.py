from __future__ import annotations

from collections.abc import Callable
from datetime import date

from .command_base import BotCommand
from .facade import StudentLifeFacade
from .models import BudgetTransaction, Note, RecurringExpense, ScheduleEvent, Task, TransactionType
from .ports import CommandRequest, CommandResponse
from .ui import example, field, h, notes_block, priority_icon, reply, title as ui_title, transaction_icon


def split_parts(args: str, expected: int, usage: str) -> list[str]:
    parts = [part.strip() for part in args.split("|")]
    if len(parts) < expected or any(not part for part in parts[:expected]):
        raise ValueError(f"Format invalid. Exemplu: {usage}")
    return parts


def append_notes(text: str, notes: list[str]) -> str:
    return text + notes_block(notes)


def format_task(task: Task, index: int | None = None) -> str:
    status = "✅" if task.completed else "⬜"
    number = f"{index}. " if index is not None else ""
    return (
        f"{status} <b>{h(number + task.title)}</b>\n"
        f"   📅 Deadline: {h(task.due_date.isoformat())}\n"
        f"   {priority_icon(task.priority.value)} Prioritate: {h(task.priority.value)}"
    )


def format_deadline(task: Task, index: int | None = None) -> str:
    days_left = (task.due_date - date.today()).days
    if days_left < 0:
        timing = f"intarziat cu {abs(days_left)} zile"
    elif days_left == 0:
        timing = "azi"
    elif days_left == 1:
        timing = "maine"
    else:
        timing = f"in {days_left} zile"
    number = f"{index}. " if index is not None else ""
    return (
        f"⏰ <b>{h(number + task.title)}</b>\n"
        f"   📅 {h(task.due_date.isoformat())} · {h(timing)}\n"
        f"   {priority_icon(task.priority.value)} Prioritate: {h(task.priority.value)}"
    )


def format_schedule(event: ScheduleEvent) -> str:
    return (
        f"🗓 <b>{h(event.weekday)} · {h(event.time)}</b>\n"
        f"   📚 {h(event.subject)}\n"
        f"   📍 {h(event.location)}"
    )


def format_transaction(transaction: BudgetTransaction) -> str:
    sign = "+" if transaction.kind == TransactionType.INCOME else "-"
    return (
        f"{transaction_icon(transaction.kind.value)} <b>{sign}{transaction.amount:.2f}</b>\n"
        f"   🏷 Categoria: {h(transaction.category)}\n"
        f"   📝 {h(transaction.description)}"
    )


def format_budget_limit_status(status: dict[str, object]) -> str:
    remaining = float(status["remaining"])
    marker = "✅"
    if float(status["percent"]) >= 100:
        marker = "🚨"
    elif float(status["percent"]) >= 80:
        marker = "⚠️"
    return (
        f"{marker} <b>{h(status['category'])}</b>\n"
        f"   💳 Folosit: {float(status['spent']):.2f} / {float(status['limit']):.2f}\n"
        f"   📊 {float(status['percent']):.0f}% · ramas: {remaining:.2f}"
    )


def format_recurring_expense(expense: RecurringExpense) -> str:
    return (
        f"🔁 <b>{h(expense.description)}</b>\n"
        f"   📤 {expense.amount:.2f} · #{h(expense.category)}\n"
        f"   📅 Ziua {expense.day_of_month} a fiecarei luni"
    )


def format_note(note: Note, index: int | None = None) -> str:
    number = f"{index}. " if index is not None else ""
    return (
        f"📝 <b>{h(number + note.title)}</b>\n"
        f"   🏷 #{h(note.tag)}\n"
        f"   {h(note.body)}"
    )


class StartCommand(BotCommand):
    name = "start"
    description = "Porneste botul si explica ideea proiectului."
    usage = "/start"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import MAIN_KEYBOARD
        return reply(
            f"{ui_title('🎓', 'Student Life Helper')}\n\n"
            "Salut! Te ajut cu taskuri, orar, buget si sfaturi rapide pentru viata de student.\n\n"
            "Alege un tab de jos sau scrie /help.",
            keyboard=MAIN_KEYBOARD
        )


class HelpCommand(BotCommand):
    name = "help"
    description = "Afiseaza comenzile disponibile."
    usage = "/help"

    def __init__(self, help_provider: Callable[[], str]) -> None:
        self._help_provider = help_provider

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import MAIN_KEYBOARD
        return reply(self._help_provider(), keyboard=MAIN_KEYBOARD)


class ProfileCommand(BotCommand):
    name = "profile"
    description = "Creeaza sau afiseaza profilul studentului."
    usage = "/profile Nume | Universitate | Facultate | Grupa | An"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        if request.args.strip().lower() == "show" or not request.args.strip():
            profile = self._facade.get_profile(request.user_id)
            if profile is None:
                return reply(
                    f"{ui_title('👤', 'Profil')}\n\n"
                    "Nu ai profil inca.\n"
                    "Apasa ✏️ Set Profile sau scrie:\n"
                    f"{example(self.usage)}"
                )
            return reply(
                f"{ui_title('👤', 'Profilul tau')}\n\n"
                f"{field('🙋', 'Nume', profile.name)}\n"
                f"{field('🏛', 'Universitate', profile.university)}\n"
                f"{field('🎯', 'Facultate', profile.faculty)}\n"
                f"{field('👥', 'Grupa', profile.group)}\n"
                f"{field('📘', 'An', profile.year)}"
            )
        name, university, faculty, group, year = split_parts(request.args, 5, self.usage)[:5]
        profile = self._facade.create_profile(request.user_id, name, university, faculty, group, year)
        return reply(
            f"{ui_title('✅', 'Profil salvat')}\n\n"
            f"{field('🙋', 'Nume', profile.name)}\n"
            f"{field('👥', 'Grupa', profile.group)}"
        )


class AddTaskCommand(BotCommand):
    name = "addtask"
    description = "Adauga un task cu termen limita si prioritate."
    usage = "/addtask Titlu | YYYY-MM-DD | low|medium|high"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        if not request.args.strip():
            return reply(
                f"{ui_title('➕', 'Adauga task')}\n\n"
                "Pentru a adauga un task, scrie:\n"
                f"{example(self.usage)}\n\n"
                "Exemplu:\n"
                f"{example('/addtask Proiect TMPS | 2026-05-10 | high')}"
            )
        task_title, due_date, priority = split_parts(request.args, 3, self.usage)[:3]
        task, notes = self._facade.add_task(request.user_id, task_title, due_date, priority)
        text = f"{ui_title('✅', 'Task adaugat')}\n\n{format_task(task)}"
        return reply(append_notes(text, notes))


class TasksCommand(BotCommand):
    name = "tasks"
    description = "Listeaza taskurile sortate dupa strategia curenta."
    usage = "/tasks"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        tasks, strategy = self._facade.list_tasks(request.user_id)
        if not tasks:
            return reply(f"{ui_title('📋', 'Taskuri')}\n\nNu ai taskuri salvate.")
        rows = "\n".join(format_task(task, index) for index, task in enumerate(tasks, start=1))
        return reply(f"{ui_title('📋', 'Taskuri')} (strategie: {h(strategy)})\n\n{rows}")


class DoneCommand(BotCommand):
    name = "done"
    description = "Marcheaza un task ca finalizat."
    usage = "/done numar_task"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        task_prefix = request.args.strip()
        if not task_prefix:
            return reply(
                f"{ui_title('✅', 'Finalizeaza task')}\n\n"
                "Scrie numarul taskului din lista /tasks.\n"
                f"Exemplu: {example(self.usage)}"
            )
        task, notes = self._facade.complete_task(request.user_id, task_prefix)
        text = f"{ui_title('✅', 'Task finalizat')}\n\n{field('📌', 'Task', task.title)}"
        return reply(append_notes(text, notes))


class StrategyCommand(BotCommand):
    name = "strategy"
    description = "Schimba strategia de sortare a taskurilor."
    usage = "/strategy deadline|priority|balanced"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        if not request.args.strip():
            strategies = " · ".join(self._facade.available_task_strategies())
            return reply(
                f"{ui_title('⚙️', 'Strategii disponibile')}\n\n"
                f"{h(strategies)}"
            )
        strategy = self._facade.set_task_strategy(request.user_id, request.args)
        return reply(f"{ui_title('⚙️', 'Strategie actualizata')}\n\n{field('📋', 'Taskuri', strategy)}")


class DeadlinesCommand(BotCommand):
    name = "deadlines"
    description = "Afiseaza deadline-urile active in ordine cronologica."
    usage = "/deadlines"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        tasks = self._facade.list_deadlines(request.user_id)
        if not tasks:
            return reply(f"{ui_title('📅', 'Deadline-uri')}\n\nNu ai deadline-uri active.")
        rows = "\n".join(format_deadline(task, index) for index, task in enumerate(tasks, start=1))
        return reply(f"{ui_title('📅', 'Deadline-uri')}\n\n{rows}")


class SearchCommand(BotCommand):
    name = "search"
    description = "Cauta in taskuri, orar si buget."
    usage = "/search text"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        if not request.args.strip():
            return reply(
                f"{ui_title('🔍', 'Cautare')}\n\n"
                "Cauta in taskuri, orar si buget.\n"
                f"Exemplu: {example('/search examen')}"
            )
        results = self._facade.search(request.user_id, request.args)
        if not results:
            return reply(
                f"{ui_title('🔍', 'Cautare')}\n\n"
                f"Nu am gasit rezultate pentru: <b>{h(request.args.strip())}</b>"
            )
        rows = "\n\n".join(f"• {h(result)}" for result in results[:10])
        return reply(f"{ui_title('🔍', 'Rezultate cautare')}\n\n{rows}")


class AddNoteCommand(BotCommand):
    name = "addnote"
    description = "Adauga o notita rapida pentru cursuri, idei sau remindere."
    usage = "/addnote Titlu | Text | tag"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        if not request.args.strip():
            return reply(
                f"{ui_title('➕', 'Adauga notita')}\n\n"
                f"Exemplu: {example('/addnote Algebra | Revazut matricele | matematica')}"
            )
        note_title, body, tag = split_parts(request.args, 3, self.usage)[:3]
        note = self._facade.add_note(request.user_id, note_title, body, tag)
        return reply(f"{ui_title('✅', 'Notita salvata')}\n\n{format_note(note)}")


class NotesCommand(BotCommand):
    name = "notes"
    description = "Afiseaza notitele salvate."
    usage = "/notes"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        notes = self._facade.list_notes(request.user_id)
        if not notes:
            return reply(f"{ui_title('📝', 'Notite')}\n\nNu ai notite salvate.")
        rows = "\n\n".join(format_note(note, index) for index, note in enumerate(notes[:10], start=1))
        return reply(f"{ui_title('📝', 'Notite')}\n\n{rows}")


class StudyPlanCommand(BotCommand):
    name = "studyplan"
    description = "Genereaza un plan de studiu pe baza taskurilor active."
    usage = "/studyplan"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        plan = self._facade.generate_study_plan(request.user_id)
        rows = "\n\n".join(f"• {h(item)}" for item in plan)
        return reply(f"{ui_title('🧭', 'Plan de studiu')}\n\n{rows}")


class GradeCalcCommand(BotCommand):
    name = "gradecalc"
    description = "Calculeaza nota necesara la examen pentru media dorita."
    usage = "/gradecalc nota_curenta | media_dorita | pondere_examen_%"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        if not request.args.strip():
            return reply(
                f"{ui_title('🎯', 'Calculator nota')}\n\n"
                f"Exemplu: {example('/gradecalc 7.5 | 8.5 | 40')}"
            )
        current, desired, weight = split_parts(request.args, 3, self.usage)[:3]
        result = self._facade.calculate_required_exam_grade(current, desired, weight)
        required = float(result["required"])
        if result["status"] == "impossible":
            message = "Ai avea nevoie de peste 10. Tinta trebuie ajustata sau trebuie recuperat prin alte activitati."
        elif result["status"] == "easy":
            message = "Tinta este foarte accesibila cu ponderea introdusa."
        else:
            message = "Tinta este posibila daca planifici bine pregatirea."
        return reply(
            f"{ui_title('🎯', 'Calculator nota')}\n\n"
            f"{field('📊', 'Nota curenta', '{:.2f}'.format(float(result['current'])))}\n"
            f"{field('🏁', 'Media dorita', '{:.2f}'.format(float(result['desired'])))}\n"
            f"{field('⚖️', 'Pondere examen', '{:.0f}%'.format(float(result['weight_percent'])))}\n"
            f"{field('🧮', 'Nota necesara', '{:.2f}'.format(required))}\n\n"
            f"💬 {h(message)}"
        )


class AddScheduleCommand(BotCommand):
    name = "addschedule"
    description = "Adauga o ora/curs in orar."
    usage = "/addschedule Luni | 10:00 | Materie | Sala"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        if not request.args.strip():
            return reply(
                f"{ui_title('➕', 'Adauga ora')}\n\n"
                "Pentru a adauga o ora in orar, scrie:\n"
                f"{example(self.usage)}\n\n"
                "Exemplu:\n"
                f"{example('/addschedule Luni | 10:00 | Matematica | A-204')}"
            )
        weekday, time_value, subject, location = split_parts(request.args, 4, self.usage)[:4]
        event = self._facade.add_schedule_event(
            request.user_id,
            weekday,
            time_value,
            subject,
            location,
        )
        return reply(f"{ui_title('✅', 'Eveniment adaugat in orar')}\n\n{format_schedule(event)}")


class ScheduleCommand(BotCommand):
    name = "schedule"
    description = "Afiseaza orarul salvat."
    usage = "/schedule"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        events = self._facade.list_schedule(request.user_id)
        if not events:
            return reply(f"{ui_title('🗓', 'Orar')}\n\nOrarul este gol.")
        rows = "\n\n".join(format_schedule(event) for event in events)
        return reply(f"{ui_title('🗓', 'Orar')}\n\n{rows}")


class BudgetCommand(BotCommand):
    name = "budget"
    description = "Adauga tranzactii sau foloseste analytics pentru buget."
    usage = "/budget income|expense | suma | categorie | descriere"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        if not request.args.strip():
            return reply(
                f"{ui_title('💰', 'Buget')}\n\n"
                "Exemple:\n"
                f"{example(self.usage)}\n"
                f"{example('/budget summary')}\n"
                f"{example('/budget report')}\n"
                f"{example('/budget limit | mancare | 900')}\n"
                f"{example('/budget recurring | 250 | transport | abonament | 20')}"
            )
        args = request.args.strip()
        lowered = args.lower()
        if lowered == "summary":
            summary = self._facade.budget_summary(request.user_id)
            return reply(
                f"{ui_title('💰', 'Buget')}\n\n"
                f"{field('📥', 'Venituri', '{:.2f}'.format(summary['income']))}\n"
                f"{field('📤', 'Cheltuieli', '{:.2f}'.format(summary['expenses']))}\n"
                f"{field('💼', 'Sold', '{:.2f}'.format(summary['balance']))}"
            )
        delegated = self._delegate_subcommand(request)
        if delegated is not None:
            return delegated
        kind, amount, category, description = split_parts(request.args, 4, self.usage)[:4]
        transaction, notes = self._facade.add_transaction(
            request.user_id,
            kind,
            amount,
            category,
            description,
        )
        text = f"{ui_title('✅', 'Tranzactie salvata')}\n\n{format_transaction(transaction)}"
        return reply(append_notes(text, notes))

    def _delegate_subcommand(self, request: CommandRequest) -> CommandResponse | None:
        parts = split_parts(request.args, 1, self.usage)
        head = parts[0].strip().lower()
        args = " | ".join(parts[1:])
        delegate_request = CommandRequest(
            user_id=request.user_id,
            user_name=request.user_name,
            command=head,
            args=args,
            raw_text=request.raw_text,
        )
        delegates: dict[str, BotCommand] = {
            "limit": BudgetLimitCommand(self._facade),
            "limits": BudgetLimitsCommand(self._facade),
            "recurring": RecurringExpenseCommand(self._facade) if args else RecurringExpensesCommand(self._facade),
            "recurente": RecurringExpensesCommand(self._facade),
            "forecast": BudgetForecastCommand(self._facade),
            "predictie": BudgetForecastCommand(self._facade),
            "report": BudgetReportCommand(self._facade),
            "raport": BudgetReportCommand(self._facade),
        }
        command = delegates.get(head)
        if command is None:
            return None
        return command.execute(delegate_request)


class BudgetLimitCommand(BotCommand):
    name = "budgetlimit"
    description = "Seteaza limita lunara pentru o categorie."
    usage = "/budgetlimit categorie | suma"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        if not request.args.strip():
            return reply(
                f"{ui_title('🏷', 'Limita buget')}\n\n"
                f"Exemplu: {example(self.usage)}"
            )
        category, amount = split_parts(request.args, 2, self.usage)[:2]
        limit = self._facade.set_budget_limit(request.user_id, category, amount)
        return reply(
            f"{ui_title('✅', 'Limita salvata')}\n\n"
            f"{field('🏷', 'Categorie', limit.category)}\n"
            f"{field('💳', 'Limita lunara', '{:.2f}'.format(limit.monthly_limit))}"
        )


class BudgetLimitsCommand(BotCommand):
    name = "budgetlimits"
    description = "Afiseaza limitele lunare pe categorii."
    usage = "/budgetlimits"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        statuses = self._facade.list_budget_limit_statuses(request.user_id)
        if not statuses:
            return reply(f"{ui_title('🏷', 'Limite buget')}\n\nNu ai limite setate.")
        rows = "\n\n".join(format_budget_limit_status(status) for status in statuses)
        return reply(f"{ui_title('🏷', 'Limite buget')}\n\n{rows}")


class RecurringExpenseCommand(BotCommand):
    name = "recurringexpense"
    description = "Adauga o cheltuiala recurenta lunara."
    usage = "/recurringexpense suma | categorie | descriere | zi_luna"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        if not request.args.strip():
            return reply(
                f"{ui_title('🔁', 'Cheltuiala recurenta')}\n\n"
                f"Exemplu: {example(self.usage)}"
            )
        amount, category, description, day = split_parts(request.args, 4, self.usage)[:4]
        expense = self._facade.add_recurring_expense(
            request.user_id,
            amount,
            category,
            description,
            day,
        )
        return reply(f"{ui_title('✅', 'Recurenta salvata')}\n\n{format_recurring_expense(expense)}")


class RecurringExpensesCommand(BotCommand):
    name = "recurringexpenses"
    description = "Listeaza cheltuielile recurente."
    usage = "/recurringexpenses"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        expenses = self._facade.list_recurring_expenses(request.user_id)
        if not expenses:
            return reply(f"{ui_title('🔁', 'Cheltuieli recurente')}\n\nNu ai cheltuieli recurente salvate.")
        rows = "\n\n".join(format_recurring_expense(expense) for expense in expenses)
        return reply(f"{ui_title('🔁', 'Cheltuieli recurente')}\n\n{rows}")


class BudgetForecastCommand(BotCommand):
    name = "budgetforecast"
    description = "Estimeaza soldul pana la finalul lunii."
    usage = "/budgetforecast"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        forecast = self._facade.budget_forecast(request.user_id)
        alerts = list(forecast["alerts"])
        alert_text = notes_block([str(item) for item in alerts])
        return reply(
            f"{ui_title('📉', 'Predictie buget')}\n\n"
            f"{field('📅', 'Luna', forecast['month'])}\n"
            f"{field('📥', 'Venituri', '{:.2f}'.format(float(forecast['income'])))}\n"
            f"{field('📤', 'Cheltuieli actuale', '{:.2f}'.format(float(forecast['expenses'])))}\n"
            f"{field('🔁', 'Recurente ramase', '{:.2f}'.format(float(forecast['recurring_remaining'])))}\n"
            f"{field('💼', 'Sold estimat', '{:.2f}'.format(float(forecast['projected_balance'])))}\n"
            f"{field('📆', 'Buget zilnic sigur', '{:.2f}'.format(float(forecast['safe_daily_budget'])))}"
            f"{alert_text}"
        )


class BudgetReportCommand(BotCommand):
    name = "budgetreport"
    description = "Afiseaza raportul lunar avansat de buget."
    usage = "/budgetreport"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        report = self._facade.budget_report(request.user_id)
        categories = dict(report["by_category"])
        category_rows = [
            f"• {h(category)}: {amount:.2f}"
            for category, amount in categories.items()
        ] or ["• Nu ai cheltuieli pe categorii in luna curenta."]
        limits = list(report["limits"])
        limit_rows = [
            format_budget_limit_status(status)
            for status in limits[:5]
        ] or ["Nu ai limite lunare setate."]
        recurring = list(report["recurring"])
        recurring_rows = [
            format_recurring_expense(expense)
            for expense in recurring[:5]
        ] or ["Nu ai recurente active."]
        alerts = [str(item) for item in list(report["alerts"])]
        return reply(
            f"{ui_title('📊', 'Raport buget')}\n\n"
            f"{field('📅', 'Luna', report['month'])}\n"
            f"{field('📥', 'Venituri', '{:.2f}'.format(float(report['income'])))}\n"
            f"{field('📤', 'Cheltuieli', '{:.2f}'.format(float(report['expenses'])))}\n"
            f"{field('💼', 'Sold estimat final luna', '{:.2f}'.format(float(report['projected_balance'])))}\n\n"
            f"<b>Categorii</b>\n" + "\n".join(category_rows) + "\n\n"
            f"<b>Limite</b>\n" + "\n\n".join(limit_rows) + "\n\n"
            f"<b>Recurente</b>\n" + "\n\n".join(recurring_rows) +
            notes_block(alerts)
        )


class TipCommand(BotCommand):
    name = "tip"
    description = "Genereaza sfaturi pentru invatare, bani sau wellbeing."
    usage = "/tip study|money|wellness"

    def __init__(self, facade: StudentLifeFacade) -> None:
        self._facade = facade

    def execute(self, request: CommandRequest) -> CommandResponse:
        if not request.args.strip():
            tips = " · ".join(self._facade.available_tip_types())
            return reply(f"{ui_title('💡', 'Tipuri disponibile')}\n\n{h(tips)}")
        return reply(f"{ui_title('💡', 'Sfat pentru student')}\n\n{h(self._facade.get_tip(request.user_id, request.args))}")



class MenuTasksCommand(BotCommand):
    name = "menutasks"
    description = "Deschide submeniul pentru Task-uri."
    usage = "/menutasks"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import TASKS_KEYBOARD
        return reply(f"{ui_title('📋', 'Task-uri')}\n\nAlege:", keyboard=TASKS_KEYBOARD)

class MenuScheduleCommand(BotCommand):
    name = "menuschedule"
    description = "Deschide submeniul pentru Orar."
    usage = "/menuschedule"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import SCHEDULE_KEYBOARD
        return reply(f"{ui_title('🗓️', 'Orar')}\n\nAlege:", keyboard=SCHEDULE_KEYBOARD)

class MenuStudyCommand(BotCommand):
    name = "menustudy"
    description = "Deschide submeniul pentru Invatare."
    usage = "/menustudy"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import STUDY_KEYBOARD
        return reply(f"{ui_title('📚', 'Invatare')}\n\nAlege:", keyboard=STUDY_KEYBOARD)

class MenuFinanceCommand(BotCommand):
    name = "menufinance"
    description = "Deschide submeniul pentru Finante."
    usage = "/menufinance"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import FINANCE_KEYBOARD
        return reply(f"{ui_title('💰', 'Finante')}\n\nAlege:", keyboard=FINANCE_KEYBOARD)

class MenuTipsCommand(BotCommand):
    name = "menutips"
    description = "Deschide submeniul pentru Sfaturi."
    usage = "/menutips"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import TIPS_KEYBOARD
        return reply(f"{ui_title('💡', 'Sfaturi')}\n\nAlege:", keyboard=TIPS_KEYBOARD)

class SettingsCommand(BotCommand):
    name = "settings"
    description = "Deschide submeniul cu setarile profilului si aplicatiei."
    usage = "/settings"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import SETTINGS_KEYBOARD
        return reply(
            f"{ui_title('⚙️', 'Setari')}\n\nAlege ce setare doresti sa modifici:",
            keyboard=SETTINGS_KEYBOARD
        )

class UnknownCommand(BotCommand):
    name = "unknown"
    description = "Comanda necunoscuta."
    usage = "/help"

    def execute(self, request: CommandRequest) -> CommandResponse:
        return reply(f"{ui_title('❓', 'Comanda necunoscuta')}\n\nScrie /help pentru lista completa.")
