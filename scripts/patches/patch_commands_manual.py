with open("student_life_helper/commands.py", "r") as f:
    lines = f.readlines()

# find StartCommand index
start_idx = next(i for i, line in enumerate(lines) if "class StartCommand" in line)
end_idx = next(i for i, line in enumerate(lines) if "class HelpCommand" in line)

replacement_lines = [
    "class StartCommand(BotCommand):\n",
    "    name = \"start\"\n",
    "    description = \"Porneste botul si explica ideea proiectului.\"\n",
    "    usage = \"/start\"\n",
    "\n",
    "    def execute(self, request: CommandRequest) -> CommandResponse:\n",
    "        from student_life_helper.adapters import MAIN_KEYBOARD\n",
    "        return reply(\n",
    "            f\"{ui_title('🎓', 'Student Life Helper')}\\n\\n\"\n",
    "            \"Salut! Te ajut cu taskuri, orar, buget si sfaturi rapide pentru viata de student.\\n\\n\"\n",
    "            \"Alege un tab de jos sau scrie /help.\",\n",
    "            keyboard=MAIN_KEYBOARD\n",
    "        )\n\n\n"
]

new_lines = lines[:start_idx] + replacement_lines + lines[end_idx:]

with open("student_life_helper/commands.py", "w") as f:
    f.writelines(new_lines)
