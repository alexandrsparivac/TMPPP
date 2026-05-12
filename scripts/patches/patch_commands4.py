import re
with open("student_life_helper/commands.py", "r") as f:
    content = f.read()

replacement = """class HelpCommand(BotCommand):
    name = "help"
    description = "Afiseaza lista de comenzi."
    usage = "/help"

    def __init__(self, get_text: Callable[[], str]) -> None:
        self._get_text = get_text

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import MAIN_KEYBOARD
        return reply(self._get_text(), keyboard=MAIN_KEYBOARD)"""

content = re.sub(r"class HelpCommand.*?return reply\(self._get_text\(\)\)", replacement, content, flags=re.DOTALL)
with open("student_life_helper/commands.py", "w") as f:
    f.write(content)
