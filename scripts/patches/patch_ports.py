import re

with open("student_life_helper/ports.py", "r") as f:
    content = f.read()

new_content = """from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommandRequest:
    user_id: str
    user_name: str
    command: str
    args: str
    raw_text: str

@dataclass(frozen=True)
class ScheduledCommand:
    delay_seconds: int
    command_name: str
    args: str = ""

@dataclass(frozen=True)
class CommandResponse:
    text: str
    parse_mode: str | None = None
    keyboard: list[list[str]] | None = None
    scheduled_action: ScheduledCommand | None = None
"""

with open("student_life_helper/ports.py", "w") as f:
    f.write(new_content)
