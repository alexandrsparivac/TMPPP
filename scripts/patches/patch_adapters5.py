import re
with open("student_life_helper/adapters.py", "r") as f:
    content = f.read()

replacement = """    async def send(self, response: CommandResponse) -> None:
        from telegram import ReplyKeyboardMarkup

        message = self._update.effective_message
        if message:
            kwargs = {"parse_mode": response.parse_mode}
            # Only update keyboard if explicitly requested; otherwise keep current
            if response.keyboard is not None:
                kwargs["reply_markup"] = ReplyKeyboardMarkup(
                    response.keyboard,
                    resize_keyboard=True,
                    is_persistent=True,
                    input_field_placeholder="Alege o actiune sau scrie o comanda...",
                )
            await message.reply_text(response.text, **kwargs)"""

content = re.sub(r"\s+async def send\(self, response: CommandResponse\) -> None:.*?(?=\Z|\n\w)", "\n" + replacement + "\n", content, flags=re.DOTALL)
with open("student_life_helper/adapters.py", "w") as f:
    f.write(content)
