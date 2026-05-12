from __future__ import annotations

from html import escape
from typing import Any

from .ports import CommandResponse


HTML = "HTML"


def h(value: Any) -> str:
    return escape(str(value), quote=False)


def reply(text: str, keyboard: list[list[str]] | None = None) -> CommandResponse:
    return CommandResponse(text=text, parse_mode=HTML, keyboard=keyboard)


def title(icon: str, text: str) -> str:
    return f"{icon} <b>{h(text)}</b>"


def field(icon: str, label: str, value: Any) -> str:
    return f"{icon} <b>{h(label)}:</b> {h(value)}"


def example(command: str) -> str:
    return f"<code>{h(command)}</code>"


def notes_block(notes: list[str]) -> str:
    if not notes:
        return ""
    rows = "\n".join(f"• {h(note)}" for note in notes)
    return "\n\n🔔 <b>Notificari</b>\n" + rows


def priority_icon(priority: str) -> str:
    return {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢",
    }.get(priority, "⚪")


def transaction_icon(kind: str) -> str:
    return "📥" if kind == "income" else "📤"
