"""
Module: atlas.modules.web_media
Purpose: Free-first web and media helpers for Atlas.
Author: NOVA Development Agent
Version: 0.1.0
Dependencies: standard library, optional requests
Last Updated: 2026-04-26
"""

from __future__ import annotations

import json
import logging
from typing import Any
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from atlas.models import AssistantResponse, RiskLevel

logger = logging.getLogger(__name__)


def _fetch_json(url: str, timeout: float = 5.0) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "AtlasAssistant/0.1"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


class WebMediaManager:
    """Handle public, low-cost web/media capabilities."""

    def weather(self, city: str) -> AssistantResponse:
        """Fetch weather from the free wttr.in endpoint."""
        location = city.strip() or "London"
        try:
            data = _fetch_json(f"https://wttr.in/{quote_plus(location)}?format=j1")
            current = data["current_condition"][0]
            message = (
                f"Weather in {location}: {current['temp_C']}C, "
                f"{current['weatherDesc'][0]['value']}, humidity {current['humidity']}%."
            )
            return AssistantResponse(True, message, "weather_info", data={"city": location})
        except (KeyError, IndexError, OSError, TimeoutError, json.JSONDecodeError) as exc:
            logger.warning("Weather lookup failed: %s", exc)
            return AssistantResponse(
                False,
                f"Weather lookup failed for {location}.",
                "weather_info",
                data={"error": str(exc)},
            )

    def web_search(self, query: str) -> AssistantResponse:
        """Return a browser-ready free search URL."""
        cleaned = query.strip()
        if not cleaned:
            return AssistantResponse(False, "Tell me what to search for.", "web_search")
        url = f"https://duckduckgo.com/?q={quote_plus(cleaned)}"
        return AssistantResponse(
            True,
            f"I prepared a free DuckDuckGo search for: {cleaned}",
            "web_search",
            data={"url": url},
        )

    def stock_prices(self, symbol: str) -> AssistantResponse:
        """Return a free finance lookup URL without requiring API credentials."""
        cleaned = (symbol or "").strip().upper()
        if not cleaned:
            return AssistantResponse(False, "Tell me the stock symbol.", "stock_prices")
        return AssistantResponse(
            True,
            f"Stock lookup prepared for {cleaned}.",
            "stock_prices",
            data={"url": f"https://finance.yahoo.com/quote/{quote_plus(cleaned)}"},
        )

    def daily_quote(self) -> AssistantResponse:
        """Return a deterministic quote for offline use."""
        return AssistantResponse(
            True,
            "Today's quote: Small, correct steps compound into powerful systems.",
            "daily_quote",
        )

    def tell_joke(self) -> AssistantResponse:
        """Return a simple offline joke."""
        return AssistantResponse(
            True,
            "Why did the Linux assistant stay calm? Because every problem had a process ID.",
            "tell_joke",
        )

    def lifestyle_tip(self, intent: str) -> AssistantResponse:
        """Return deterministic guidance for wellness and lifestyle intents."""
        tips = {
            "meditation": "Try a two-minute breathing cycle: inhale four, hold four, exhale six.",
            "workout_plan": "Start with 5 minutes mobility, 3 bodyweight circuits, then stretch.",
            "diet_plan": "Build meals around protein, vegetables, slow carbs, and water.",
            "recipes": "Tell me ingredients next, and I can suggest a simple recipe.",
            "pet_care": "Keep water fresh, track appetite, and call a vet for sudden behavior changes.",
            "plant_care": "Check soil moisture before watering; most plants dislike wet roots.",
            "home_decor": "Use one main color, one accent color, and warm lighting.",
            "fashion_tips": "Fit matters first; then match color temperature and occasion.",
            "makeup_tips": "Start light, blend well, and match products to skin type.",
        }
        return AssistantResponse(True, tips.get(intent, "I can help with that topic."), intent)

    def unsupported_social_integration(self, platform: str) -> AssistantResponse:
        """Explain safe path for social platform automation."""
        return AssistantResponse(
            False,
            (
                f"{platform} automation needs official APIs, OAuth, or your authorized browser "
                "session. Atlas will not bypass login walls or private backends."
            ),
            f"{platform.lower()}_integration",
            RiskLevel.CONFIRM,
            data={"safe_path": "official_api_or_user_authorized_export"},
        )
