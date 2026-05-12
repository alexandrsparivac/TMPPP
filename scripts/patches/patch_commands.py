import re

with open("student_life_helper/commands.py", "r") as f:
    content = f.read()

replacement = """
class SettingsCommand(BotCommand):
    name = "settings"
    description = "Deschide submeniul cu setarile profilului si aplicatiei."
    usage = "/settings"

    def execute(self, request: CommandRequest) -> CommandResponse:
        from student_life_helper.adapters import SETTINGS_KEYBOARD
        return reply(
            f"{ui_title('⚙️', 'Setari')}\\n\\nAlege ce setare doresti sa modifici:",
            keyboard=SETTINGS_KEYBOARD
        )

class UnknownCommand"""

new_content = content.replace("class UnknownCommand", replacement)

with open("student_life_helper/commands.py", "w") as f:
    f.write(new_content)
