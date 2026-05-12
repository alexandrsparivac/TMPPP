from __future__ import annotations

import urllib.parse
import urllib.request
from typing import Protocol


class ExplanationService(Protocol):
    def explain(self, topic: str) -> str:
        ...


class PollinationsExplanationService:
    """External AI client kept outside commands for easier replacement/testing."""

    def explain(self, topic: str) -> str:
        encoded_topic = urllib.parse.quote(topic)
        url = (
            "https://text.pollinations.ai/prompt/"
            "Explica+scurt+si+clar+ca+pentru+un+student+urmatorul+concept:+"
            f"{encoded_topic}"
        )
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.read().decode("utf-8")
