with open("student_life_helper/commands.py", "r") as f:
    content = f.read()

replacement = """class MenuTasksCommand(BotCommand):
    name = "menutasks"
    description = "Deschide submeniul pentru Task-uri."
    usage = "/menutasks"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import TASKS_KEYBOARD
        return reply(f"{ui_title('📋', 'Task-uri')}\\n\\nAlege:", keyboard=TASKS_KEYBOARD)

class MenuScheduleCommand(BotCommand):
    name = "menuschedule"
    description = "Deschide submeniul pentru Orar."
    usage = "/menuschedule"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import SCHEDULE_KEYBOARD
        return reply(f"{ui_title('🗓️', 'Orar')}\\n\\nAlege:", keyboard=SCHEDULE_KEYBOARD)

class MenuStudyCommand(BotCommand):
    name = "menustudy"
    description = "Deschide submeniul pentru Invatare."
    usage = "/menustudy"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import STUDY_KEYBOARD
        return reply(f"{ui_title('📚', 'Invatare')}\\n\\nAlege:", keyboard=STUDY_KEYBOARD)

class MenuFinanceCommand(BotCommand):
    name = "menufinance"
    description = "Deschide submeniul pentru Finante."
    usage = "/menufinance"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import FINANCE_KEYBOARD
        return reply(f"{ui_title('💰', 'Finante')}\\n\\nAlege:", keyboard=FINANCE_KEYBOARD)

class MenuTipsCommand(BotCommand):
    name = "menutips"
    description = "Deschide submeniul pentru Sfaturi."
    usage = "/menutips"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import TIPS_KEYBOARD
        return reply(f"{ui_title('💡', 'Sfaturi')}\\n\\nAlege:", keyboard=TIPS_KEYBOARD)

class SettingsCommand"""

content = content.replace("class SettingsCommand", replacement)
with open("student_life_helper/commands.py", "w") as f:
    f.write(content)
