import re
with open("student_life_helper/conversations.py", "r") as f:
    content = f.read()

content = re.sub(r'class AddHabitStrategy.*?keyboard=PRODUCTIVITY_KEYBOARD\)', '', content, flags=re.DOTALL)
content = re.sub(r'# Register in ConversationManager.*?new_strategies', '', content, flags=re.DOTALL)
content = content.replace('"""\n\n\n\n\n\n"""', "")

with open("student_life_helper/conversations.py", "w") as f:
    f.write(content)
