from __future__ import annotations

import logging

from .command_base import BotCommand
from .ports import CommandRequest, CommandResponse
from .ui import example, h, reply, title as ui_title


class CommandDecorator(BotCommand):
    """Decorator: adds behavior around a command without changing it."""

    def __init__(self, wrapped: BotCommand) -> None:
        self._wrapped = wrapped
        self.name = wrapped.name
        self.description = wrapped.description
        self.usage = wrapped.usage

    def execute(self, request: CommandRequest) -> CommandResponse:
        return self._wrapped.execute(request)


class LoggingCommandDecorator(CommandDecorator):
    def execute(self, request: CommandRequest) -> CommandResponse:
        logging.info("Command /%s from user %s", self.name, request.user_id)
        return self._wrapped.execute(request)


class ErrorHandlingCommandDecorator(CommandDecorator):
    def execute(self, request: CommandRequest) -> CommandResponse:
        try:
            return self._wrapped.execute(request)
        except ValueError as exc:
            hint = f"\n\nUtilizare: {example(self.usage)}" if self.usage else ""
            return reply(f"{ui_title('⚠️', 'Eroare')}\n\n{h(exc)}{hint}")
        except Exception as exc:
            logging.exception("Unexpected command error")
            return reply(f"{ui_title('⚠️', 'Eroare neasteptata')}\n\n{h(exc)}")
