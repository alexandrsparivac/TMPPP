from __future__ import annotations

from dataclasses import replace
from typing import Any

from .conversations import CANCEL_COMMAND, TEXT_COMMAND, CompletedForm, ConversationManager
from .factories import BaseCommandFactory
from .ports import CommandRequest, CommandResponse


class BotRouter:
    def __init__(
        self,
        command_factory: BaseCommandFactory,
        conversations: ConversationManager,
        facade: Any = None,
    ) -> None:
        self._command_factory = command_factory
        self._conversations = conversations
        self.facade = facade

    def handle(self, request: CommandRequest) -> CommandResponse:
        if request.command == CANCEL_COMMAND:
            return self._conversations.cancel(request.user_id)

        if self._conversations.has_active(request.user_id):
            if request.command == TEXT_COMMAND:
                result = self._conversations.accept_answer(request)
                if isinstance(result, CompletedForm):
                    final_request = replace(
                        request,
                        command=result.command,
                        args=result.args,
                        raw_text=f"/{result.command} {result.args}",
                    )
                    return self._execute(final_request)
                return result
            self._conversations.cancel(request.user_id)

        if request.command == TEXT_COMMAND:
            return CommandResponse("Alege un tab sau scrie /help pentru lista comenzilor.")

        command_name = request.command or "help"
        if self._conversations.should_start(command_name, request.args):
            form_request = replace(request, command=command_name)
            return self._conversations.start(form_request)

        return self._execute(request)

    def _execute(self, request: CommandRequest) -> CommandResponse:
        command_name = request.command or "help"
        command = self._command_factory.get_command(command_name)
        return command.execute(request)
