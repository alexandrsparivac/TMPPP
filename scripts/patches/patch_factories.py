import re

with open("student_life_helper/factories.py", "r") as f:
    content = f.read()

imports_patch = "import student_life_helper.commands as cmds\nimport student_life_helper.commands_productivity as prod_cmds"
content = content.replace("import student_life_helper.commands as cmds", imports_patch)

factory_patch = """            "addhabit": (prod_cmds.HabitsCommand, True),  # Form trigger doesn't actually use command instance directly for execution until finished, but it needs to exist
            "menuproductivity": (prod_cmds.MenuProductivityCommand, False),
            "pomodorostart": (prod_cmds.StartPomodoroCommand, False),
            "pomodorodone": (prod_cmds.PomodoroDoneCommand, False),
            "habits": (prod_cmds.HabitsCommand, True),
            "loghabit": (prod_cmds.LogHabitCommand, True),
"""
content = re.sub(
    r"(\s+)\"menutasks\":", 
    r"\1" + factory_patch.strip() + r"\n\1\"menutasks\":", 
    content
)

with open("student_life_helper/factories.py", "w") as f:
    f.write(content)
