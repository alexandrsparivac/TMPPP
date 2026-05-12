import re

with open("student_life_helper/conversations.py", "r") as f:
    content = f.read()

forms_patch = """            "addhabit": FormSpec(
                command="addhabit",
                steps=[
                    FormStep("name", "Numele obiceiului (ex: Citește 10 pagini):", required("Numele obiceiului"))
                ],
                build_args=lambda answers: answers["name"],
            ),
            "loghabit": FormSpec(
                command="loghabit",
                steps=[
                    FormStep("prefix", "Scrie primele litere din ID-ul sau numele obiceiului pentru a-l bifa azi:", lambda x: x)
                ],
                build_args=lambda answers: answers["prefix"],
            ),
            "profile": FormSpec("""

content = content.replace('"profile": FormSpec(', forms_patch)

with open("student_life_helper/conversations.py", "w") as f:
    f.write(content)
