import re
with open("student_life_helper/conversations.py", "r") as f:
    content = f.read()

content = re.sub(r'class LogHabitStrategy.*?keyboard=PRODUCTIVITY_KEYBOARD\)', '', content, flags=re.DOTALL)
with open("student_life_helper/conversations.py", "w") as f:
    f.write(content)
