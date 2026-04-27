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
import json
import os
import re
from typing import Any, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from atlas.capabilities import capability_by_name
from atlas.core.config import AtlasSettings, ProviderOption, default_settings
from atlas.models import Intent, RiskLevel


@dataclass(frozen=True)
class BrainProviderStatus:
    """Configured AI brain provider status."""

    preferred: str
    configured: tuple[str, ...]
    free_first: tuple[str, ...]
    bilingual_languages: tuple[str, ...]
    female_voice: str


class AIPlannerClient(Protocol):
    """HTTP client interface used by hosted AI planners."""

    def post_json(
        self,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Post JSON and return a decoded JSON object."""


class UrlLibAIClient:
    """Tiny urllib JSON client to avoid adding hosted-AI SDK dependencies."""

    def __init__(self, timeout: float = 10.0) -> None:
        """Initialize with request timeout."""
        self.timeout = timeout

    def post_json(
        self,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Post JSON and return decoded response."""
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "AtlasAssistant/0.9",
                **(headers or {}),
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                decoded = response.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            raise RuntimeError(f"Hosted AI request failed: {error}") from error
        parsed = json.loads(decoded)
        if not isinstance(parsed, dict):
            raise RuntimeError("Hosted AI returned non-object JSON.")
        return parsed


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
        client: AIPlannerClient | None = None,
    ) -> None:
        """Initialize the planner."""
        self.settings = settings or default_settings()
        self.env = env or os.environ
        self.client = client or UrlLibAIClient()

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
        """Return a planned intent from local rules or hosted free-tier providers."""
        local_plan = self.plan_local(text)
        if local_plan is not None:
            return local_plan
        return self.plan_hosted(text)

    def plan_local(self, text: str) -> Intent | None:
        """Return a deterministic local plan, if recognized."""
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

    def plan_hosted(self, text: str) -> Intent | None:
        """Use Gemini first, then Groq, when API keys are configured."""
        if self.env.get("GEMINI_API_KEY"):
            plan = self._plan_with_gemini(text, self.env["GEMINI_API_KEY"])
            if plan is not None:
                return plan
        if self.env.get("GROQ_API_KEY"):
            return self._plan_with_groq(text, self.env["GROQ_API_KEY"])
        return None

    def _plan_with_gemini(self, text: str, api_key: str) -> Intent | None:
        """Request a structured intent from Gemini free-tier API."""
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={api_key}"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": _planner_prompt(text)}],
                }
            ],
            "generationConfig": {"temperature": 0.0, "responseMimeType": "application/json"},
        }
        try:
            response = self.client.post_json(url, payload)
            raw_text = _extract_gemini_text(response)
            return _intent_from_hosted_json(raw_text, text, "gemini")
        except (KeyError, RuntimeError, ValueError, json.JSONDecodeError):
            return None

    def _plan_with_groq(self, text: str, api_key: str) -> Intent | None:
        """Request a structured intent from Groq OpenAI-compatible API."""
        payload = {
            "model": "llama-3.1-8b-instant",
            "temperature": 0,
            "messages": [
                {"role": "system", "content": _planner_system_prompt()},
                {"role": "user", "content": text},
            ],
            "response_format": {"type": "json_object"},
        }
        try:
            response = self.client.post_json(
                "https://api.groq.com/openai/v1/chat/completions",
                payload,
                headers={"Authorization": f"Bearer {api_key}"},
            )
            raw_text = str(response["choices"][0]["message"]["content"])
            return _intent_from_hosted_json(raw_text, text, "groq")
        except (KeyError, RuntimeError, ValueError, json.JSONDecodeError):
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


def _planner_system_prompt() -> str:
    """Return strict instructions for hosted planners."""
    return (
        "You are Atlas, a Linux desktop assistant planner. Return only JSON. "
        "Schema: {\"intent\":\"name\",\"args\":{...},\"language\":\"en|hi|ur\"}. "
        "Use only existing Atlas intents. Do not invent commands. If unsure, "
        "return {\"intent\":\"unknown\",\"args\":{},\"language\":\"en\"}."
    )


def _planner_prompt(text: str) -> str:
    """Return Gemini planner prompt."""
    return (
        f"{_planner_system_prompt()}\n"
        "Useful intents include web_search, weather_info, daily_news, page_summary, "
        "youtube_metadata, volume_control, brightness_control, app_launcher, "
        "downloads_folder, todo_list, timer, pomodoro_timer, dictionary, "
        "git_status, safe_shell, system_diagnostics.\n"
        f"User command: {text}"
    )


def _extract_gemini_text(response: dict[str, Any]) -> str:
    """Extract text part from Gemini response."""
    return str(response["candidates"][0]["content"]["parts"][0]["text"])


def _intent_from_hosted_json(raw_text: str, original_text: str, provider: str) -> Intent | None:
    """Validate hosted JSON and return a safe Atlas intent."""
    parsed = json.loads(_strip_json_fence(raw_text))
    if not isinstance(parsed, dict):
        return None
    intent_name = str(parsed.get("intent", "unknown")).strip()
    if intent_name == "unknown":
        return None
    capability = capability_by_name(intent_name)
    if capability is None or capability.risk == RiskLevel.DANGEROUS:
        return None
    args = parsed.get("args", {})
    if not isinstance(args, dict):
        return None
    safe_args = _safe_args(args)
    safe_args["planned_by"] = provider
    language = str(parsed.get("language", _detect_language(_normalize(original_text))))
    if language not in {"en", "hi", "ur"}:
        language = "en"
    return Intent(
        intent_name,
        capability.category,
        0.78,
        language=language,
        args=safe_args,
        raw_text=original_text,
    )


def _strip_json_fence(raw_text: str) -> str:
    """Remove common Markdown JSON fences."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned


def _safe_args(args: dict[str, Any]) -> dict[str, str | int | float | bool]:
    """Keep only JSON scalar args accepted by Atlas tools."""
    safe: dict[str, str | int | float | bool] = {}
    for key, value in args.items():
        if not isinstance(key, str):
            continue
        if isinstance(value, bool | int | float | str):
            safe[key] = value
    return safe
