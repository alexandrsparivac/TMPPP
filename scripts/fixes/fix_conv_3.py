with open("student_life_helper/conversations.py", "r") as f:
    content = f.read()

lines = content.split('\n')
valid_lines = lines[:-5]

with open("student_life_helper/conversations.py", "w") as f:
    f.write('\n'.join(valid_lines))
