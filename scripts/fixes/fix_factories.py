import re
with open("student_life_helper/factories.py", "r") as f:
    content = f.read()

content = content.replace('\\"menutasks\\":', '"menutasks":')

with open("student_life_helper/factories.py", "w") as f:
    f.write(content)
