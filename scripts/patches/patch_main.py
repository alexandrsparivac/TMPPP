import re

with open("student_life_helper/__main__.py", "r") as f:
    content = f.read()

demo_replacement = """import threading
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
"""

telegram_replacement = """    async def handle_message(update, context) -> None:
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

    application = Application.builder().token(config.bot_token).build()"""

content = re.sub(r"def run_demo\(\) -> None:.*?        adapter.send\(response\)", demo_replacement, content, flags=re.DOTALL)
content = re.sub(r"    async def handle_message\(update, context\) -> None:.*?    application = Application\.builder\(\)\.token\(config\.bot_token\)\.build\(\)", telegram_replacement, content, flags=re.DOTALL)


with open("student_life_helper/__main__.py", "w") as f:
    f.write(content)
