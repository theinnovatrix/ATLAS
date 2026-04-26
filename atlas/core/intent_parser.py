"""
Module: atlas.core.intent_parser
Purpose: Parse English, Hindi, and Urdu text commands into Atlas intents.
Author: NOVA Development Agent
Version: 0.1.0
Dependencies: atlas.models
Last Updated: 2026-04-26
"""

from __future__ import annotations

import re
from typing import Iterable

from atlas.models import Intent


class IntentParser:
    """Rule-based bilingual parser for the first Atlas command milestone."""

    _PATTERNS: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
        ("system_info", "system", "en", ("system info", "pc details", "computer details")),
        ("system_info", "system", "hi", ("system batao", "pc details batao", "computer batao")),
        ("system_info", "system", "ur", ("nizam batao", "computer ki tafseel", "pc ki maloomat")),
        ("volume_control", "system", "en", ("volume", "sound")),
        ("volume_control", "system", "hi", ("awaz", "awaaz", "volume")),
        ("volume_control", "system", "ur", ("awaz", "volume")),
        ("brightness_control", "system", "en", ("brightness", "screen light")),
        ("brightness_control", "system", "hi", ("brightness", "roshni", "screen ki light")),
        ("brightness_control", "system", "ur", ("brightness", "roshni", "screen light")),
        ("app_launcher", "system", "en", ("open app", "launch", "open firefox", "open terminal")),
        ("app_launcher", "system", "hi", ("app kholo", "firefox kholo", "terminal kholo")),
        ("app_launcher", "system", "ur", ("app kholo", "firefox kholo", "terminal kholo")),
        ("calculator", "productivity", "en", ("calculate", "what is", "solve")),
        ("calculator", "productivity", "hi", ("hisab", "calculate", "kitna")),
        ("calculator", "productivity", "ur", ("hisab", "calculate", "kitna")),
        ("translate_text", "productivity", "en", ("translate",)),
        ("translate_text", "productivity", "hi", ("anuvad", "translate", "tarjuma")),
        ("translate_text", "productivity", "ur", ("tarjuma", "translate")),
        ("weather_info", "web", "en", ("weather",)),
        ("weather_info", "web", "hi", ("mausam", "weather")),
        ("weather_info", "web", "ur", ("mausam", "weather")),
        ("web_search", "web", "en", ("search", "find online", "look up")),
        ("web_search", "web", "hi", ("search karo", "dhundo", "talash")),
        ("web_search", "web", "ur", ("search karo", "dhundo", "talash")),
        ("quick_note", "productivity", "en", ("note", "remember")),
        ("quick_note", "productivity", "hi", ("note banao", "yaad rakho")),
        ("quick_note", "productivity", "ur", ("note banao", "yaad rakho")),
        ("capabilities", "help", "en", ("features", "capabilities", "what can you do")),
        ("capabilities", "help", "hi", ("kya kar sakti", "features batao")),
        ("capabilities", "help", "ur", ("kya kar sakti", "features batao")),
    )

    def parse(self, text: str) -> Intent:
        """Return the most likely intent for a user command."""
        normalized = _normalize(text)
        best: tuple[str, str, str, float] | None = None
        for name, category, language, phrases in self._PATTERNS:
            score = _score(normalized, phrases)
            if score and (best is None or score > best[3]):
                best = (name, category, language, score)

        if best is None:
            return Intent(
                name="unknown",
                category="unknown",
                confidence=0.0,
                language=_detect_language(normalized),
                args={},
                raw_text=text,
            )

        name, category, language, confidence = best
        return Intent(
            name=name,
            category=category,
            confidence=confidence,
            language=language,
            args=_extract_args(name, normalized),
            raw_text=text,
        )


def _normalize(text: str) -> str:
    """Normalize command text for simple matching."""
    return re.sub(r"\s+", " ", text.casefold().strip())


def _score(text: str, phrases: Iterable[str]) -> float:
    """Score phrase matches without external NLP dependencies."""
    for phrase in phrases:
        if phrase in text:
            return min(1.0, 0.65 + len(phrase) / max(len(text), 1))
    return 0.0


def _detect_language(text: str) -> str:
    """Best-effort language hint for Latin-script English, Hindi, and Urdu commands."""
    hindi_urdu_markers = ("karo", "kholo", "batao", "mausam", "awaz", "roshni", "kitna")
    if any(marker in text for marker in hindi_urdu_markers):
        return "hi"
    return "en"


def _extract_args(intent_name: str, text: str) -> dict[str, str | int]:
    """Extract lightweight command arguments for implemented intents."""
    if intent_name in {"volume_control", "brightness_control"}:
        number = re.search(r"\b(\d{1,3})\b", text)
        if number:
            return {"level": max(0, min(100, int(number.group(1))))}
        if any(word in text for word in ("up", "increase", "tez", "zyada")):
            return {"level": 80}
        if any(word in text for word in ("down", "decrease", "kam", "low")):
            return {"level": 35}
    if intent_name == "app_launcher":
        for prefix in ("open app", "open", "launch", "app kholo"):
            if prefix in text:
                return {"app": text.split(prefix, 1)[1].strip() or "terminal"}
    if intent_name == "calculator":
        expression = re.sub(r"^(calculate|solve|what is|hisab|kitna)\s+", "", text).strip()
        return {"expression": expression}
    if intent_name == "weather_info":
        city = text
        for word in ("weather", "mausam", "batao", "ka", "ki"):
            city = city.replace(word, " ")
        return {"target": re.sub(r"\s+", " ", city).strip() or "London"}
    if intent_name in {"web_search", "quick_note", "translate_text"}:
        query = text
        for word in ("search", "search karo", "dhundo", "talash", "note", "remember", "translate"):
            query = query.replace(word, " ")
        return {"target": re.sub(r"\s+", " ", query).strip()}
    return {}
