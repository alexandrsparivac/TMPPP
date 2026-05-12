from __future__ import annotations

from typing import Any

from .conversations import CANCEL_COMMAND, FORM_TRIGGER, TEXT_COMMAND
from .ports import CommandRequest, CommandResponse


MAIN_KEYBOARD = [
    ["📋 Task-uri", "🗓️ Orar"],
    ["📚 Invatare", "💰 Finante"],
    ["💡 Sfaturi", "⚙️ Setari"],
    ["🍅 Start Pomodoro", "📅 Obiceiuri"],
    ["🤖 Intreaba (AI)"],
    ["🏠 Start", "❓ Help"]
]

TASKS_KEYBOARD = [
    ["📑 Lista Taskuri", "➕ Adauga Task", "✅ Finalizeaza"],
    ["📅 Deadlines", "🔍 Cauta"],
    ["🔙 Inapoi"]
]

SCHEDULE_KEYBOARD = [
    ["🗓 Afiseaza Orar", "➕ Adauga Lectie"],
    ["🔙 Inapoi"]
]

STUDY_KEYBOARD = [
    ["📝 Notite", "➕ Adauga Notita"],
    ["🧭 Plan de Studiu", "🎯 Calculator Note"],
    ["🤖 Explica-mi"],
    ["🔙 Inapoi"]
]

FINANCE_KEYBOARD = [
    ["💰 Adauga Tranzactie", "🧾 Sumar Buget"],
    ["📊 Raport Buget", "📉 Predictie Buget"],
    ["🏷 Limita Categorie", "🏷 Limite Buget"],
    ["🔁 Adauga Recurenta", "🔁 Recurente"],
    ["🔙 Inapoi"]
]

TIPS_KEYBOARD = [
    ["💡 Sfat Aleatoriu"],
    ["📚 Sfat Invatare", "💸 Sfat Financiar", "🧘 Sfat Wellness"],
    ["🔙 Inapoi"]
]


HABITS_KEYBOARD = [
    ["📑 Lista Obiceiuri", "➕ Adauga Obicei"],
    ["✅ Bifeaza Obicei"],
    ["🔙 Inapoi"]
]

PRODUCTIVITY_KEYBOARD = [
    ["🍅 Start Pomodoro", "📅 Obiceiuri"],
    ["🔙 Inapoi"]
]

SETTINGS_KEYBOARD = [
    ["👁 Profilul Meu", "✏️ Seteaza Profil", "⚙️ Schimba Strategie"],
    ["🔙 Inapoi"]
]

BUTTON_COMMANDS = {
    # Old Keyboard Fallbacks (to ensure seamless transition)
    "📋 tasks": ("tasks", ""),
    "🗓 schedule": ("schedule", ""),
    "📚 invatare": ("menustudy", ""),
    "💰 budget": ("budget", FORM_TRIGGER),
    "💡 tips": ("tip", FORM_TRIGGER),
    "⚙️ strategy": ("strategy", FORM_TRIGGER),
    "👤 profile": ("profile", "show"),
    "👁 profile": ("profile", "show"),
    "✏️ set profile": ("profile", FORM_TRIGGER),
    "➕ add task": ("addtask", FORM_TRIGGER),
    "✅ done": ("done", FORM_TRIGGER),
    "📅 deadlines": ("deadlines", ""),
    "🔍 search": ("search", FORM_TRIGGER),
    "📝 notes": ("notes", ""),
    "➕ add note": ("addnote", FORM_TRIGGER),
    "🧭 study plan": ("studyplan", ""),
    "🎯 grade calc": ("gradecalc", FORM_TRIGGER),
    "➕ add lesson": ("addschedule", FORM_TRIGGER),
    "🧾 budget summary": ("budget", "summary"),
    "📊 budget report": ("budgetreport", ""),
    "📉 budget forecast": ("budgetforecast", ""),
    "📚 study tip": ("tip", "study"),
    "💸 money tip": ("tip", "money"),
    "🧘 wellness tip": ("tip", "wellness"),

    # Main categories (open submenus)
    "📋 task-uri": ("menutasks", ""),
    "task": ("menutasks", ""),
    "tasks": ("menutasks", ""),
    "taskuri": ("menutasks", ""),
    "🗓️ orar": ("menuschedule", ""),
    "orar": ("menuschedule", ""),
    "schedule": ("menuschedule", ""),
    "📚 invatare": ("menustudy", ""),
    "invatare": ("menustudy", ""),
    "study": ("menustudy", ""),
    "studiu": ("menustudy", ""),
    "💰 finante": ("menufinance", ""),
    "finante": ("menufinance", ""),
    "buget": ("menufinance", ""),
    "bani": ("menufinance", ""),
    "💡 sfaturi": ("menutips", ""),
    "sfaturi": ("menutips", ""),
    "tips": ("menutips", ""),
    "⚙️ setari": ("settings", ""),
    "setari": ("settings", ""),
    "settings": ("settings", ""),
    "🤖 intreaba (ai)": ("explain", FORM_TRIGGER),
    "intreaba (ai)": ("explain", FORM_TRIGGER),
    "🤖 intreaba ai": ("explain", FORM_TRIGGER),
    "intreaba ai": ("explain", FORM_TRIGGER),
    "intreaba-ma": ("explain", FORM_TRIGGER),
    "intreabama": ("explain", FORM_TRIGGER),
    "ai": ("explain", FORM_TRIGGER),
    "🏠 start": ("start", ""),
    "start": ("start", ""),
    "❓ help": ("help", ""),
    "help": ("help", ""),
    "🔙 inapoi": ("start", ""),
    "inapoi": ("start", ""),
    "❌ cancel": (CANCEL_COMMAND, ""),
    "cancel": (CANCEL_COMMAND, ""),

    # Tasks Actions
    "📑 lista taskuri": ("tasks", ""),
    "lista taskuri": ("tasks", ""),
    "➕ adauga task": ("addtask", FORM_TRIGGER),
    "adauga task": ("addtask", FORM_TRIGGER),
    "✅ finalizeaza": ("done", FORM_TRIGGER),
    "finalizeaza": ("done", FORM_TRIGGER),
    "🔍 cauta": ("search", FORM_TRIGGER),
    "cauta": ("search", FORM_TRIGGER),

    # Schedule Actions
    "🗓 afiseaza orar": ("schedule", ""),
    "afiseaza orar": ("schedule", ""),
    "➕ adauga lectie": ("addschedule", FORM_TRIGGER),
    "adauga lectie": ("addschedule", FORM_TRIGGER),

    # Study Actions
    "📝 notite": ("notes", ""),
    "notite": ("notes", ""),
    "➕ adauga notita": ("addnote", FORM_TRIGGER),
    "adauga notita": ("addnote", FORM_TRIGGER),
    "🧭 plan de studiu": ("studyplan", ""),
    "plan de studiu": ("studyplan", ""),
    "🎯 calculator note": ("gradecalc", FORM_TRIGGER),
    "calculator note": ("gradecalc", FORM_TRIGGER),
    "🤖 explica-mi": ("explain", FORM_TRIGGER),
    "explica-mi": ("explain", FORM_TRIGGER),

    # Finance Actions
    "💰 adauga tranzactie": ("budget", FORM_TRIGGER),
    "adauga tranzactie": ("budget", FORM_TRIGGER),
    "🧾 sumar buget": ("budget", "summary"),
    "sumar buget": ("budget", "summary"),
    "📊 raport buget": ("budgetreport", ""),
    "raport buget": ("budgetreport", ""),
    "📉 predictie buget": ("budgetforecast", ""),
    "predictie buget": ("budgetforecast", ""),
    "🏷 limita categorie": ("budgetlimit", FORM_TRIGGER),
    "limita categorie": ("budgetlimit", FORM_TRIGGER),
    "🏷 limite buget": ("budgetlimits", ""),
    "limite buget": ("budgetlimits", ""),
    "🔁 adauga recurenta": ("recurringexpense", FORM_TRIGGER),
    "adauga recurenta": ("recurringexpense", FORM_TRIGGER),
    "🔁 recurente": ("recurringexpenses", ""),
    "recurente": ("recurringexpenses", ""),

    # Tips Actions
    "💡 sfat aleatoriu": ("tip", ""),
    "sfat aleatoriu": ("tip", ""),
    "📚 sfat invatare": ("tip", "study"),
    "sfat invatare": ("tip", "study"),
    "💸 sfat financiar": ("tip", "money"),
    "sfat financiar": ("tip", "money"),
    "🧘 sfat wellness": ("tip", "wellness"),
    "sfat wellness": ("tip", "wellness"),


    # Productivity Actions
    "⚡️ productivitate": ("menuproductivity", ""),
    "productivitate": ("menuproductivity", ""),
    "🍅 start pomodoro": ("pomodorostart", FORM_TRIGGER),
    "start pomodoro": ("pomodorostart", FORM_TRIGGER),
    "📅 obiceiuri": ("menuhabits", ""),
    "obiceiuri": ("menuhabits", ""),
    "📑 lista obiceiuri": ("habits", ""),
    "lista obiceiuri": ("habits", ""),
    "➕ adauga obicei": ("addhabit", FORM_TRIGGER),
    "adauga obicei": ("addhabit", FORM_TRIGGER),
    "✅ bifeaza obicei": ("loghabit", FORM_TRIGGER),
    "bifeaza obicei": ("loghabit", FORM_TRIGGER),
    # Settings Actions
    "👁 profilul meu": ("profile", "show"),
    "profilul meu": ("profile", "show"),
    "✏️ seteaza profil": ("profile", FORM_TRIGGER),
    "seteaza profil": ("profile", FORM_TRIGGER),
    "⚙️ schimba strategie": ("strategy", FORM_TRIGGER),
    "schimba strategie": ("strategy", FORM_TRIGGER),
}


def parse_command_text(text: str) -> tuple[str, str]:
    cleaned = text.strip()
    if not cleaned:
        return "help", ""
    button_command = BUTTON_COMMANDS.get(cleaned.lower())
    if button_command:
        return button_command
    if not cleaned.startswith("/"):
        return TEXT_COMMAND, cleaned
    head, separator, tail = cleaned[1:].partition(" ")
    command = head.split("@", 1)[0].lower()
    return command, tail if separator else ""


class ConsoleAdapter:
    """Adapter: converts terminal input/output to the bot request format."""

    def to_request(
        self,
        line: str,
        user_id: str = "console-user",
        user_name: str = "Demo Student",
    ) -> CommandRequest:
        command, args = parse_command_text(line)
        return CommandRequest(
            user_id=user_id,
            user_name=user_name,
            command=command,
            args=args,
            raw_text=line,
        )

    def send(self, response: CommandResponse) -> None:
        print(response.text)


class TelegramUpdateAdapter:
    """Adapter: hides python-telegram-bot objects from the domain code."""

    def __init__(self, update: Any, context: Any) -> None:
        self._update = update
        self._context = context

    def to_request(self) -> CommandRequest:
        user = self._update.effective_user
        message = self._update.effective_message
        text = message.text if message and message.text else ""
        command, args = parse_command_text(text)
        return CommandRequest(
            user_id=str(user.id) if user else "unknown",
            user_name=user.full_name if user else "Student",
            command=command,
            args=args,
            raw_text=text,
        )
    async def send(self, response: CommandResponse) -> None:
        from telegram import ReplyKeyboardMarkup

        message = self._update.effective_message
        if message:
            kwargs = {"parse_mode": response.parse_mode}
            # Only update keyboard if explicitly requested; otherwise keep current
            if response.keyboard is not None:
                kwargs["reply_markup"] = ReplyKeyboardMarkup(
                    response.keyboard,
                    resize_keyboard=True,
                    is_persistent=True,
                    input_field_placeholder="Alege o actiune sau scrie o comanda...",
                )
            await message.reply_text(response.text, **kwargs)
