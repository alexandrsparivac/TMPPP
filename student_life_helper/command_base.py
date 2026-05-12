from __future__ import annotations

from abc import ABC, abstractmethod

from .ports import CommandRequest, CommandResponse


class BotCommand(ABC):
    """Command pattern: every bot action is represented as an object."""

    name: str = ""
    description: str = ""
    usage: str = ""

    @abstractmethod
    def execute(self, request: CommandRequest) -> CommandResponse:
        raise NotImplementedError
