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
        ("file_opener", "system", "en", ("open file", "open folder", "open path")),
        ("file_opener", "system", "hi", ("file kholo", "folder kholo")),
        ("file_opener", "system", "ur", ("file kholo", "folder kholo")),
        (
            "system_diagnostics",
            "system",
            "en",
            ("system diagnostics", "system dependencies", "dependency check", "check tools"),
        ),
        ("system_diagnostics", "system", "hi", ("system diagnostics", "tools check")),
        ("system_diagnostics", "system", "ur", ("system diagnostics", "tools check")),
        ("notifications", "system", "en", ("notify", "notification", "send notification")),
        ("notifications", "system", "hi", ("notification bhejo", "notify")),
        ("notifications", "system", "ur", ("notification bhejo", "notify")),
        ("screenshot", "system", "en", ("screenshot", "screen shot")),
        ("lock_screen", "system", "en", ("lock screen", "lock pc", "lock computer")),
        ("service_status", "system", "en", ("service status", "system service", "service")),
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
        ("timer", "productivity", "en", ("timer", "set timer")),
        ("timer", "productivity", "hi", ("timer lagao", "timer")),
        ("timer", "productivity", "ur", ("timer lagao", "timer")),
        ("todo_list", "productivity", "en", ("todo", "to do", "task")),
        ("todo_list", "productivity", "hi", ("kaam likho", "todo", "task")),
        ("todo_list", "productivity", "ur", ("kaam likho", "todo", "task")),
        ("dictionary", "productivity", "en", ("define", "meaning", "dictionary")),
        ("dictionary", "productivity", "hi", ("matlab", "meaning", "dictionary")),
        ("dictionary", "productivity", "ur", ("matlab", "meaning", "dictionary")),
        ("voice_status", "voice", "en", ("voice status", "audio status", "speech status")),
        ("voice_status", "voice", "hi", ("voice status", "audio status", "awaz status")),
        ("voice_status", "voice", "ur", ("voice status", "audio status", "awaz status")),
        ("speech_to_text", "voice", "en", ("transcribe", "speech to text")),
        ("speech_to_text", "voice", "hi", ("transcribe", "speech to text", "awaz likho")),
        ("speech_to_text", "voice", "ur", ("transcribe", "speech to text", "awaz likho")),
        ("text_to_speech", "voice", "en", ("say", "speak", "text to speech")),
        ("text_to_speech", "voice", "hi", ("bolo", "speak", "text to speech")),
        ("text_to_speech", "voice", "ur", ("bolo", "speak", "text to speech")),
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
    extractors = {
        "volume_control": _extract_level,
        "brightness_control": _extract_level,
        "app_launcher": _extract_app,
        "file_opener": _extract_path_target,
        "notifications": _extract_notification_target,
        "service_status": _extract_service_target,
        "calculator": _extract_expression,
        "weather_info": _extract_weather_target,
        "web_search": _extract_text_target,
        "quick_note": _extract_text_target,
        "translate_text": _extract_text_target,
        "todo_list": _extract_todo_target,
        "dictionary": _extract_dictionary_target,
        "timer": _extract_minutes,
        "speech_to_text": _extract_prefixed_target,
        "text_to_speech": _extract_prefixed_target,
    }
    extractor = extractors.get(intent_name)
    return extractor(text) if extractor else {}


def _extract_level(text: str) -> dict[str, int]:
    """Extract a percentage level."""
    number = re.search(r"\b(\d{1,3})\b", text)
    if number:
        return {"level": max(0, min(100, int(number.group(1))))}
    if any(word in text for word in ("up", "increase", "tez", "zyada")):
        return {"level": 80}
    if any(word in text for word in ("down", "decrease", "kam", "low")):
        return {"level": 35}
    return {}


def _extract_app(text: str) -> dict[str, str]:
    """Extract an app name."""
    for prefix in ("open app", "open", "launch", "app kholo"):
        if prefix in text:
            return {"app": text.split(prefix, 1)[1].strip() or "terminal"}
    return {}


def _extract_path_target(text: str) -> dict[str, str]:
    """Extract a file or folder path."""
    return {"path": _strip_prefix(text, ("open file", "open folder", "open path", "file kholo", "folder kholo"))}


def _extract_notification_target(text: str) -> dict[str, str]:
    """Extract notification text."""
    target = _strip_prefix(text, ("send notification", "notification", "notify", "notification bhejo"))
    return {"target": target or "Atlas notification"}


def _extract_service_target(text: str) -> dict[str, str]:
    """Extract a systemd service name."""
    if text.startswith("service ") and text.endswith(" status"):
        target = text.removeprefix("service ").removesuffix(" status").strip()
        return {"target": target or "ssh"}
    target = _strip_prefix(text, ("service status", "system service", "service"))
    return {"target": target or "ssh"}


def _extract_expression(text: str) -> dict[str, str]:
    """Extract a calculator expression."""
    expression = re.sub(r"^(calculate|solve|what is|hisab|kitna)\s+", "", text).strip()
    return {"expression": expression}


def _extract_weather_target(text: str) -> dict[str, str]:
    """Extract a city from a weather command."""
    return {"target": _strip_words(text, ("weather", "mausam", "batao", "ka", "ki")) or "London"}


def _extract_text_target(text: str) -> dict[str, str]:
    """Extract a free-form text target."""
    words = (
        "search",
        "search karo",
        "dhundo",
        "talash",
        "note",
        "remember",
        "translate",
        "transcribe",
        "speech to text",
        "awaz likho",
        "say",
        "speak",
        "text to speech",
        "bolo",
    )
    return {"target": _strip_words(text, words)}


def _extract_todo_target(text: str) -> dict[str, str]:
    """Extract a todo item or leave empty to list todos."""
    target = _strip_words(text, ("add todo", "todo add", "todo", "to do", "task", "kaam likho"))
    return {"target": target}


def _extract_dictionary_target(text: str) -> dict[str, str]:
    """Extract a word to define."""
    return {"target": _strip_words(text, ("define", "meaning", "dictionary", "matlab"))}


def _extract_minutes(text: str) -> dict[str, int]:
    """Extract timer minutes."""
    number = re.search(r"\b(\d{1,3})\b", text)
    return {"minutes": int(number.group(1)) if number else 5}


def _strip_words(text: str, words: tuple[str, ...]) -> str:
    """Remove command words and normalize whitespace."""
    cleaned = text
    for word in words:
        cleaned = cleaned.replace(word, " ")
    return re.sub(r"\s+", " ", cleaned).strip()


def _strip_prefix(text: str, prefixes: tuple[str, ...]) -> str:
    """Remove a command prefix without modifying the rest of the target."""
    for prefix in prefixes:
        if text.startswith(prefix):
            return text[len(prefix):].strip()
    return text.strip()


def _extract_prefixed_target(text: str) -> dict[str, str]:
    """Extract text after a voice command prefix without mutating paths."""
    prefixes = (
        "speech to text",
        "text to speech",
        "awaz likho",
        "transcribe",
        "speak",
        "bolo",
        "say",
    )
    for prefix in prefixes:
        if text.startswith(prefix):
            return {"target": text[len(prefix):].strip()}
    return {"target": text}
