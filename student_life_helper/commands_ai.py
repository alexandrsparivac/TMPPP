from __future__ import annotations

from .ai import ExplanationService, PollinationsExplanationService
from .command_base import BotCommand
from .ports import CommandRequest, CommandResponse


class ExplainCommand(BotCommand):
    name = "explain"
    description = "Explica un concept folosind AI."
    usage = "/explain concept"

    def __init__(self, explanation_service: ExplanationService | None = None) -> None:
        self._explanation_service = explanation_service or PollinationsExplanationService()

    def execute(self, request: CommandRequest) -> CommandResponse:
        topic = request.args.strip()
        if not topic:
            return CommandResponse(text="Te rog sa imi spui ce doresti sa iti explic.")

        try:
            explanation = self._explanation_service.explain(topic)
        except Exception:
            explanation = (
                "Din pacate, am intampinat o eroare la conectarea cu AI-ul. "
                "Incearca din nou mai tarziu."
            )

        return CommandResponse(
            text=f"🤖 **Explicatie pentru:** {topic}\n\n{explanation}",
            parse_mode="Markdown",
        )
