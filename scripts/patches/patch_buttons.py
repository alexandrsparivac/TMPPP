import re
with open("student_life_helper/adapters.py", "r") as f:
    content = f.read()

new_buttons = """BUTTON_COMMANDS = {
    # Old Keyboard Fallbacks (to ensure seamless transition)
    "📋 tasks": ("menutasks", ""),
    "🗓 schedule": ("menuschedule", ""),
    "📚 invatare": ("menustudy", ""),
    "💰 budget": ("menufinance", ""),
    "💡 tips": ("menutips", ""),
    "⚙️ strategy": ("strategy", FORM_TRIGGER),
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
