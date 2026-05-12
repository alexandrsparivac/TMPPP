import re

with open("student_life_helper/adapters.py", "r") as f:
    content = f.read()

# Update handle_request to also check for scheduled_action
handle_request_code = """    def handle_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.message.text:
            return

        user = update.message.from_user
        user_id = str(user.id)
        user_name = user.first_name

        text = update.message.text
        # Fallback to CANCEL if a command is run midway through a form
        if text.startswith("/") and len(text) > 1:
            cmd = text[1:].split()[0].lower()
            args = text[len(cmd) + 2 :].strip()
        else:
            cmd, args = BUTTON_COMMANDS.get(text.lower(), ("unknown", text))

        request = CommandRequest(user_id=user_id, user_name=user_name, command=cmd, args=args, raw_text=text)

        try:
            response = self.router.route(request)
            self._send_response(update, response)
            
            if response.scheduled_action:
                self._schedule_telegram_job(context, user_id, user_name, response.scheduled_action)

        except Exception as e:
            update.message.reply_text(str(e))

    def _schedule_telegram_job(self, context: ContextTypes.DEFAULT_TYPE, user_id: str, user_name: str, action: Any) -> None:
        def job_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
            job = context.job
            req = CommandRequest(user_id=job.data["user_id"], user_name=job.data["user_name"], command=job.data["command_name"], args=job.data["args"], raw_text="")
            try:
                resp = self.router.route(req)
                # Instead of update.message.reply_text, we use context.bot.send_message
                kwargs = {"chat_id": job.data["user_id"], "text": resp.text}
                if resp.parse_mode:
                    kwargs["parse_mode"] = resp.parse_mode
                if resp.keyboard:
                    kwargs["reply_markup"] = ReplyKeyboardMarkup(resp.keyboard, resize_keyboard=True)
                context.bot.send_message(**kwargs)
            except Exception as e:
                context.bot.send_message(chat_id=job.data["user_id"], text=str(e))
                
        context.job_queue.run_once(
            job_callback, 
            action.delay_seconds, 
            data={"user_id": user_id, "user_name": user_name, "command_name": action.command_name, "args": action.args}
        )

    def _send_response(self, update: Update, response: CommandResponse) -> None:"""

content = re.sub(r"    def handle_request\(self, update: Update, context: ContextTypes\.DEFAULT_TYPE\) -> None:.*?    def _send_response\(self, update: Update, response: CommandResponse\) -> None:", handle_request_code, content, flags=re.DOTALL)

with open("student_life_helper/adapters.py", "w") as f:
    f.write(content)
