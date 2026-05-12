from __future__ import annotations

import unittest

from student_life_helper.commands_ai import ExplainCommand
from student_life_helper.ports import CommandRequest


class FakeExplanationService:
    def explain(self, topic: str) -> str:
        return f"Explicatie test pentru {topic}"


class ExplainCommandTest(unittest.TestCase):
    def test_explain_uses_injected_service(self) -> None:
        command = ExplainCommand(FakeExplanationService())
        response = command.execute(
            CommandRequest(
                user_id="u1",
                user_name="Ana",
                command="explain",
                args="polimorfism",
                raw_text="/explain polimorfism",
            )
        )

        self.assertIn("polimorfism", response.text)
        self.assertIn("Explicatie test", response.text)
        self.assertEqual("Markdown", response.parse_mode)


if __name__ == "__main__":
    unittest.main()
