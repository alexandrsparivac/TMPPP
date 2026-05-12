with open("student_life_helper/conversations.py", "r") as f:
    content = f.read()

# We tried to add strategies to conversation.py, but conversation.py in this architecture 
# uses FormSpec mapped in _build_forms. The ConversationStrategy classes were meant to be 
# part of a different ConversationManager architecture.

import re
content = re.sub(r'class AddHabitStrategy.*?LogHabitStrategy\(self\.facade\),', '', content, flags=re.DOTALL)
content = content.replace("            SetProfileStrategy(self.facade),", "")
content = content.replace("            AddHabitStrategy(self.facade),", "")
content = content.replace("            LogHabitStrategy(self.facade),", "")


with open("student_life_helper/conversations.py", "w") as f:
    f.write(content)
