import re

with open("student_life_helper/adapters.py", "r") as f:
    content = f.read()

# Add Productivity Keyboard
productivity_kb = """
PRODUCTIVITY_KEYBOARD = [
    ["🍅 Start Pomodoro"],
    ["📅 Obiceiuri", "➕ Adauga Obicei"],
    ["✅ Bifeaza Obicei"],
    ["🔙 Inapoi"]
]
"""
content = content.replace("SETTINGS_KEYBOARD = [", productivity_kb + "SETTINGS_KEYBOARD = [")

# Add MAIN_KEYBOARD button for productivity
content = content.replace('["🏠 Start", "❓ Help"]', '["⚡️ Productivitate"],\n    ["🏠 Start", "❓ Help"]')

# Add BUTTON_COMMANDS mapping
productivity_commands = """
    # Productivity Actions
    "⚡️ productivitate": ("menuproductivity", ""),
    "productivitate": ("menuproductivity", ""),
    "🍅 start pomodoro": ("pomodorostart", ""),
    "start pomodoro": ("pomodorostart", ""),
    "📅 obiceiuri": ("habits", ""),
    "obiceiuri": ("habits", ""),
    "➕ adauga obicei": ("addhabit", FORM_TRIGGER),
    "adauga obicei": ("addhabit", FORM_TRIGGER),
    "✅ bifeaza obicei": ("loghabit", FORM_TRIGGER),
    "bifeaza obicei": ("loghabit", FORM_TRIGGER),
"""
content = content.replace("    # Settings Actions", productivity_commands + "    # Settings Actions")

with open("student_life_helper/adapters.py", "w") as f:
    f.write(content)
