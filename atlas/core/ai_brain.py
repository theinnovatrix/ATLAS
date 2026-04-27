"""
Module: atlas.core.ai_brain
Purpose: Free-first flexible command planner for Atlas.
Author: NOVA Development Agent
Version: 0.8.0
Dependencies: standard library, atlas.models
Last Updated: 2026-04-27
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import re
from typing import Mapping

from atlas.core.config import AtlasSettings, ProviderOption, default_settings
from atlas.models import Intent


@dataclass(frozen=True)
class BrainProviderStatus:
    """Configured AI brain provider status."""

    preferred: str
    configured: tuple[str, ...]
    free_first: tuple[str, ...]
    bilingual_languages: tuple[str, ...]
    female_voice: str


class FreeFirstBrain:
    """Plan flexible natural-language commands into Atlas intents.

    The milestone intentionally provides deterministic local planning first.
    Gemini and Groq are configured as free/low-cost hosted upgrade slots, but
    no network call is required for tests or offline use.
    """

    def __init__(
        self,
        settings: AtlasSettings | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        """Initialize the planner."""
        self.settings = settings or default_settings()
        self.env = env or os.environ

    def provider_status(self) -> BrainProviderStatus:
        """Return free-first AI provider state."""
        configured = tuple(
            option.name for option in self.settings.llm_options if option.is_configured(self.env)
        )
        free_first = tuple(option.name for option in self.settings.llm_options[:3])
        return BrainProviderStatus(
            preferred=self.settings.preferred_llm,
            configured=configured,
            free_first=free_first,
            bilingual_languages=(self.settings.default_language, *self.settings.secondary_languages),
            female_voice=self.settings.preferred_voice,
        )

    def provider_options(self) -> tuple[ProviderOption, ...]:
        """Return available LLM provider definitions."""
        return self.settings.llm_options

    def plan(self, text: str) -> Intent | None:
        """Return a planned intent for flexible natural language, if recognized."""
        normalized = _normalize(text)
        if not normalized:
            return None

        if _contains_any(normalized, ("lower", "decrease", "kam")) and _contains_any(
            normalized, ("volume", "sound", "awaz")
        ):
            return Intent(
                "volume_control",
                "system",
                0.62,
                language=_detect_language(normalized),
                args={"level": 35, "planned_by": "free_first_brain"},
                raw_text=text,
            )
        if _contains_any(normalized, ("increase", "raise", "up", "zyada")) and _contains_any(
            normalized, ("volume", "sound", "awaz")
        ):
            return Intent(
                "volume_control",
                "system",
                0.62,
                language=_detect_language(normalized),
                args={"level": 80, "planned_by": "free_first_brain"},
                raw_text=text,
            )
        if "open" in normalized and "download" in normalized:
            return Intent(
                "downloads_folder",
                "desktop",
                0.65,
                language=_detect_language(normalized),
                args={"planned_by": "free_first_brain"},
                raw_text=text,
            )
        if "summarize" in normalized and "http" in normalized:
            url = _first_url(normalized)
            return Intent(
                "page_summary",
                "web",
                0.7,
                args={"target": url, "planned_by": "free_first_brain"},
                raw_text=text,
            )
        if _contains_any(normalized, ("search", "look up", "find online")):
            query = re.sub(r"\b(please|search|look up|find online|for)\b", " ", normalized).strip()
            return Intent(
                "web_search",
                "web",
                0.6,
                args={"target": _squash(query), "planned_by": "free_first_brain"},
                raw_text=text,
            )
        if _contains_any(normalized, ("what can you do", "help me", "madad")):
            return Intent(
                "capabilities",
                "help",
                0.6,
                language=_detect_language(normalized),
                args={"planned_by": "free_first_brain"},
                raw_text=text,
            )
        return None


def _normalize(text: str) -> str:
    """Normalize planning text."""
    return re.sub(r"\s+", " ", text.casefold().strip())


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    """Return whether any phrase appears in text."""
    return any(needle in text for needle in needles)


def _first_url(text: str) -> str:
    """Extract the first URL-like token."""
    for token in text.split():
        if token.startswith(("http://", "https://")):
            return token
    return ""


def _squash(text: str) -> str:
    """Normalize repeated whitespace."""
    return re.sub(r"\s+", " ", text).strip()


def _detect_language(text: str) -> str:
    """Best-effort English/Hindi/Urdu marker detection."""
    if _contains_any(text, ("karo", "kholo", "batao", "kam", "zyada", "madad")):
        return "hi"
    return "en"
