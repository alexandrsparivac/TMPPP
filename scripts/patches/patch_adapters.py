import re

with open("student_life_helper/adapters.py", "r") as f:
    content = f.read()

# Replace the MAIN_KEYBOARD and SETTINGS_KEYBOARD section
keyboards_text = """MAIN_KEYBOARD = [
    ["📋 Task-uri", "🗓️ Orar"],
    ["📚 Invatare", "💰 Finante"],
    ["💡 Sfaturi", "⚙️ Setari"],
    ["🏠 Start", "❓ Help"]
]

TASKS_KEYBOARD = [
    ["📋 Tasks", "➕ Add Task", "✅ Done"],
    ["📅 Deadlines", "🔍 Search"],
    ["🔙 Inapoi"]
]

SCHEDULE_KEYBOARD = [
    ["🗓 Schedule", "➕ Add Lesson"],
    ["🔙 Inapoi"]
]

STUDY_KEYBOARD = [
    ["📝 Notes", "➕ Add Note"],
    ["🧭 Study Plan", "🎯 Grade Calc"],
    ["🔙 Inapoi"]
]

FINANCE_KEYBOARD = [
    ["💰 Budget", "🧾 Budget Summary"],
    ["🔙 Inapoi"]
]

TIPS_KEYBOARD = [
    ["💡 Tips"],
    ["📚 Study Tip", "💸 Money Tip", "🧘 Wellness Tip"],
    ["🔙 Inapoi"]
]

SETTINGS_KEYBOARD = [
    ["👁 Profile", "✏️ Set Profile", "⚙️ Strategy"],
    ["🔙 Inapoi"]
]
"""

content = re.sub(
    r"MAIN_KEYBOARD = \[.*?\]\s+SETTINGS_KEYBOARD = \[.*?\]",
    keyboards_text,
    content,
    flags=re.DOTALL
)

# Add button mappings for the new categories
menu_mappings = """    "⚙️ setari": ("settings", ""),
    "📋 task-uri": ("menutasks", ""),
    "🗓️ orar": ("menuschedule", ""),
    "📚 invatare": ("menustudy", ""),
    "💰 finante": ("menufinance", ""),
    "💡 sfaturi": ("menutips", ""),"""

content = content.replace('"⚙️ setari": ("settings", ""),', menu_mappings)

with open("student_life_helper/adapters.py", "w") as f:
    f.write(content)
