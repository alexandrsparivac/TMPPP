import re

with open("student_life_helper/adapters.py", "r") as f:
    content = f.read()

# Replace the keyboards section completely
new_keyboards = """MAIN_KEYBOARD = [
    ["📋 Task-uri", "🗓️ Orar"],
    ["📚 Invatare", "💰 Finante"],
    ["💡 Sfaturi", "⚙️ Setari"],
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
    ["🔙 Inapoi"]
]

FINANCE_KEYBOARD = [
    ["💰 Adauga Tranzactie", "🧾 Sumar Buget"],
    ["🔙 Inapoi"]
]

TIPS_KEYBOARD = [
    ["💡 Sfat Aleatoriu"],
    ["📚 Sfat Invatare", "💸 Sfat Financiar", "🧘 Sfat Wellness"],
    ["🔙 Inapoi"]
]

SETTINGS_KEYBOARD = [
    ["👁 Profilul Meu", "✏️ Seteaza Profil", "⚙️ Schimba Strategie"],
    ["🔙 Inapoi"]
]
"""

content = re.sub(
    r"MAIN_KEYBOARD = \[.*?\]\s*TASKS_KEYBOARD = \[.*?\]\s*SCHEDULE_KEYBOARD = \[.*?\]\s*STUDY_KEYBOARD = \[.*?\]\s*FINANCE_KEYBOARD = \[.*?\]\s*TIPS_KEYBOARD = \[.*?\]\s*SETTINGS_KEYBOARD = \[.*?\]",
    new_keyboards,
    content,
    flags=re.DOTALL
)

# Rewrite BUTTON_COMMANDS entirely to match the new buttons and triggers
new_buttons = """BUTTON_COMMANDS = {
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
    "📅 deadlines": ("deadlines", ""),
    "deadlines": ("deadlines", ""),
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

    # Finance Actions
    "💰 adauga tranzactie": ("budget", FORM_TRIGGER),
    "adauga tranzactie": ("budget", FORM_TRIGGER),
    "🧾 sumar buget": ("budget", "summary"),
    "sumar buget": ("budget", "summary"),

    # Tips Actions
    "💡 sfat aleatoriu": ("tip", ""),
    "sfat aleatoriu": ("tip", ""),
    "📚 sfat invatare": ("tip", "study"),
    "sfat invatare": ("tip", "study"),
    "💸 sfat financiar": ("tip", "money"),
    "sfat financiar": ("tip", "money"),
    "🧘 sfat wellness": ("tip", "wellness"),
    "sfat wellness": ("tip", "wellness"),

    # Settings Actions
    "👁 profilul meu": ("profile", "show"),
    "profilul meu": ("profile", "show"),
    "✏️ seteaza profil": ("profile", FORM_TRIGGER),
    "seteaza profil": ("profile", FORM_TRIGGER),
    "⚙️ schimba strategie": ("strategy", FORM_TRIGGER),
    "schimba strategie": ("strategy", FORM_TRIGGER),
}
"""

content = re.sub(
    r"BUTTON_COMMANDS = \{.*?\}\n",
    new_buttons,
    content,
    flags=re.DOTALL
)

with open("student_life_helper/adapters.py", "w") as f:
    f.write(content)
