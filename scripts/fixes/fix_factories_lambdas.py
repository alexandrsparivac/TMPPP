import re
with open("student_life_helper/factories.py", "r") as f:
    content = f.read()

content = content.replace('"addhabit": (prod_cmds.HabitsCommand, True),  # Form trigger doesn\'t actually use command instance directly for execution until finished, but it needs to exist', '"addhabit": lambda: prod_cmds.HabitsCommand(self._facade),')
content = content.replace('"menuproductivity": (prod_cmds.MenuProductivityCommand, False),', '"menuproductivity": lambda: prod_cmds.MenuProductivityCommand(),')
content = content.replace('"pomodorostart": (prod_cmds.StartPomodoroCommand, False),', '"pomodorostart": lambda: prod_cmds.StartPomodoroCommand(),')
content = content.replace('"pomodorodone": (prod_cmds.PomodoroDoneCommand, False),', '"pomodorodone": lambda: prod_cmds.PomodoroDoneCommand(),')
content = content.replace('"habits": (prod_cmds.HabitsCommand, True),', '"habits": lambda: prod_cmds.HabitsCommand(self._facade),')
content = content.replace('"loghabit": (prod_cmds.LogHabitCommand, True),', '"loghabit": lambda: prod_cmds.LogHabitCommand(self._facade),')

with open("student_life_helper/factories.py", "w") as f:
    f.write(content)
