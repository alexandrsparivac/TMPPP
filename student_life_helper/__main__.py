from __future__ import annotations

import logging
import sys

from .adapters import ConsoleAdapter, TelegramUpdateAdapter
from .app import build_router
from .config import AppConfig


import threading
import time
from .ports import CommandRequest

def run_demo() -> None:
    router = build_router()
    adapter = ConsoleAdapter()
    print("Student Life Helper demo. Scrie /help sau exit.")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            print()
            return
        if line.lower() in {"exit", "quit"}:
            return
        if not line:
            continue
        req = adapter.to_request(line)
        response = router.handle(req)
        adapter.send(response)
        if response.scheduled_action:
            def delay_run(uid, uname, cmd, args, delay):
                time.sleep(delay)
                job_req = CommandRequest(user_id=uid, user_name=uname, command=cmd, args=args, raw_text="")
                res = router.handle(job_req)
                adapter.send(res)
            t = threading.Thread(target=delay_run, args=(req.user_id, req.user_name, response.scheduled_action.command_name, response.scheduled_action.args, response.scheduled_action.delay_seconds))
            t.daemon = True
            t.start()



def run_telegram() -> None:
    try:
        from telegram.ext import Application, MessageHandler, filters
    except ImportError as exc:
        raise SystemExit("Instaleaza dependintele: pip install -r requirements.txt") from exc

    config = AppConfig.load()
    if not config.bot_token:
        raise SystemExit("Lipseste BOT_TOKEN. Exemplu: BOT_TOKEN=123:abc python -m student_life_helper telegram")

    router = build_router()
    import datetime

    async def check_reminders(context_job):
        facade = router.facade
        if not facade:
            return
        users = facade.get_all_users()
        now = datetime.datetime.now()
        thirty_mins_from_now = now + datetime.timedelta(minutes=30)
        now_time = now.strftime("%H:%M")
        thirty_time = thirty_mins_from_now.strftime("%H:%M")
        days = ["Luni", "Marti", "Miercuri", "Joi", "Vineri", "Sambata", "Duminica"]
        today_weekday = days[now.weekday()]

        for user_id in users:
            schedule = facade.list_schedule(user_id)
            for ev in schedule:
                if ev.weekday == today_weekday and ev.time == thirty_time:
                    await context_job.bot.send_message(
                        chat_id=user_id,
                        text=f"🔔 Reminder: Peste 30 minute ai cursul {ev.subject} in {ev.location}!"
                    )
            
            if now_time == "23:30":
                tasks = facade.list_deadlines(user_id)
                today_date = now.date()
                for t in tasks:
                    if not t.completed and t.due_date == today_date:
                        await context_job.bot.send_message(
                            chat_id=user_id,
                            text=f"⏰ Reminder Task: Deadline-ul pentru '{t.title}' expira la miezul noptii!"
                        )

    async def morning_report(context_job):
        facade = router.facade
        if not facade:
            return
        users = facade.get_all_users()
        now = datetime.datetime.now()
        days = ["Luni", "Marti", "Miercuri", "Joi", "Vineri", "Sambata", "Duminica"]
        today_weekday = days[now.weekday()]
        today_date = now.date()

        for user_id in users:
            schedule = facade.list_schedule(user_id)
            today_courses = [ev for ev in schedule if ev.weekday == today_weekday]
            tasks = facade.list_deadlines(user_id)
            today_tasks = [t for t in tasks if not t.completed and t.due_date == today_date]
            
            if today_courses or today_tasks:
                msg = f"🌅 Buna dimineata! Azi ai {len(today_courses)} cursuri si {len(today_tasks)} deadline-uri. Succes!"
                await context_job.bot.send_message(chat_id=user_id, text=msg)

    async def handle_message(update, context) -> None:
        adapter = TelegramUpdateAdapter(update, context)
        req = adapter.to_request()
        response = router.handle(req)
        await adapter.send(response)
        if response.scheduled_action:
            async def job_callback(context_job):
                job = context_job.job
                from .ports import CommandRequest
                job_req = CommandRequest(
                    user_id=job.data["user_id"],
                    user_name=job.data["user_name"],
                    command=job.data["command"],
                    args=job.data["args"],
                    raw_text=""
                )
                res = router.handle(job_req)
                kwargs = {"chat_id": job.data["user_id"], "text": res.text}
                if res.parse_mode:
                    kwargs["parse_mode"] = res.parse_mode
                await context_job.bot.send_message(**kwargs)
            
            context.job_queue.run_once(
                job_callback,
                response.scheduled_action.delay_seconds,
                data={
                    "user_id": req.user_id,
                    "user_name": req.user_name,
                    "command": response.scheduled_action.command_name,
                    "args": response.scheduled_action.args,
                }
            )

    application = Application.builder().token(config.bot_token).build()
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    application.job_queue.run_repeating(check_reminders, interval=60, first=10)
    application.job_queue.run_daily(morning_report, time=datetime.time(hour=8, minute=0, second=0))
    application.run_polling()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    mode = sys.argv[1] if len(sys.argv) > 1 else "demo"
    if mode == "demo":
        run_demo()
    elif mode == "telegram":
        run_telegram()
    else:
        raise SystemExit("Mod necunoscut. Foloseste: demo sau telegram")


if __name__ == "__main__":
    main()
