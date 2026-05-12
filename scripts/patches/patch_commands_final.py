import re
with open("student_life_helper/commands.py", "r") as f:
    content = f.read()

replacement = """class StartCommand(BotCommand):
    name = "start"
    description = "Porneste botul si explica ideea proiectului."
    usage = "/start"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import MAIN_KEYBOARD
        return reply(
            f"{ui_title('🎓', 'Student Life Helper')}\\n\\n"
            "Salut! Te ajut cu taskuri, orar, buget si sfaturi rapide pentru viata de student.\\n\\n"
            "Alege un tab de jos sau scrie /help.",
            keyboard=MAIN_KEYBOARD
        )"""

content = re.sub(r"class StartCommand\(BotCommand\):.*?def execute.*?return reply\(.*?\n\s*\)", replacement, content, flags=re.DOTALL)
with open("student_life_helper/commands.py", "w") as f:
    f.write(content)
