"""
Module: atlas.modules.web_media
Purpose: Safe, free-first web and media helpers for Atlas.
Author: NOVA Development Agent
Version: 0.5.0
Dependencies: standard library
Last Updated: 2026-04-27
"""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
import json
import logging
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote_plus, urlparse
from urllib.request import Request, urlopen

from atlas.models import AssistantResponse, RiskLevel

logger = logging.getLogger(__name__)


class WebRequestError(RuntimeError):
    """Raised when a web request fails after retry attempts."""


@dataclass
class WebClient:
    """Small urllib-backed client with retry and timeout defaults."""

    user_agent: str = "AtlasAssistant/0.5"
    retries: int = 2
    timeout: float = 5.0
    backoff_seconds: float = 0.1

    def get_json(self, url: str) -> dict[str, Any]:
        """Fetch and parse JSON with retry."""
        body = self.get_text(url)
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as error:
            raise WebRequestError(f"Invalid JSON from {url}: {error}") from error
        if not isinstance(parsed, dict):
            raise WebRequestError(f"Expected JSON object from {url}")
        return parsed

    def get_text(self, url: str) -> str:
        """Fetch text with retry and timeout."""
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                request = Request(url, headers={"User-Agent": self.user_agent})
                with urlopen(request, timeout=self.timeout) as response:
                    return response.read().decode("utf-8", errors="replace")
            except (HTTPError, URLError, TimeoutError, OSError) as error:
                last_error = error
                if attempt < self.retries:
                    time.sleep(self.backoff_seconds * (attempt + 1))
        raise WebRequestError(f"Request failed for {url}: {last_error}")


class _TextExtractor(HTMLParser):
    """Extract page title and visible text from simple public HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self._in_title = False
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "title":
            self._in_title = True
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        if self._in_title:
            self.title_parts.append(cleaned)
        elif not self._skip_depth:
            self.text_parts.append(cleaned)


class WebMediaManager:
    """Handle public, low-cost web/media capabilities."""

    def __init__(self, client: WebClient | None = None, env: dict[str, str] | None = None) -> None:
        """Initialize web adapters with injectable network client and environment."""
        self.client = client or WebClient()
        self.env = env if env is not None else dict(os.environ)

    def weather(self, city: str) -> AssistantResponse:
        """Fetch weather from the free wttr.in endpoint."""
        location = city.strip().casefold() or "london"
        try:
            data = self.client.get_json(f"https://wttr.in/{quote_plus(location)}?format=j1")
            current = data["current_condition"][0]
            message = (
                f"Weather in {location}: {current['temp_C']}C, "
                f"{current['weatherDesc'][0]['value']}, humidity {current['humidity']}%."
            )
            return AssistantResponse(True, message, "weather_info", data={"city": location})
        except (KeyError, IndexError, WebRequestError) as exc:
            logger.warning("Weather lookup failed: %s", exc)
            return AssistantResponse(
                False,
                f"Weather lookup failed for {location}.",
                "weather_info",
                data={"city": location, "error": str(exc)},
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
            data={"query": cleaned, "url": url, "provider": "duckduckgo"},
        )

    def daily_news(self, query: str = "world") -> AssistantResponse:
        """Fetch headlines from a public RSS endpoint with validation."""
        topic = query.strip() or "world"
        url = f"https://news.google.com/rss/search?q={quote_plus(topic)}"
        try:
            rss = self.client.get_text(url)
        except WebRequestError as exc:
            return AssistantResponse(False, f"News lookup failed for {topic}.", "daily_news", data={"error": str(exc)})
        headlines = _extract_rss_titles(rss)
        if not headlines:
            return AssistantResponse(False, f"No headlines found for {topic}.", "daily_news", data={"topic": topic})
        return AssistantResponse(
            True,
            "Top headline: " + headlines[0],
            "daily_news",
            data={
                "topic": topic,
                "headlines": headlines[:5],
                "articles": [{"title": headline} for headline in headlines[:5]],
                "provider": "google_news_rss",
            },
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

    def youtube_metadata(self, target: str) -> AssistantResponse:
        """Return YouTube metadata through official API when configured, else a safe search URL."""
        cleaned = target.strip()
        if not cleaned:
            return AssistantResponse(False, "Tell me the YouTube video or search query.", "youtube_metadata")
        video_id = _extract_youtube_video_id(cleaned)
        api_key = self.env.get("YOUTUBE_API_KEY", "")
        if not api_key:
            query = video_id or cleaned
            return AssistantResponse(
                True,
                f"YouTube lookup prepared for: {query}",
                "youtube_metadata",
                data={
                    "url": f"https://www.youtube.com/results?search_query={quote_plus(query)}",
                    "safe_path": "official_youtube_api_when_keyed",
                    "requires_key": False,
                },
            )
        if not video_id:
            return AssistantResponse(
                False,
                "Official YouTube metadata requires a video URL or id when YOUTUBE_API_KEY is set.",
                "youtube_metadata",
            )
        url = (
            "https://www.googleapis.com/youtube/v3/videos"
            f"?part=snippet,statistics&id={quote_plus(video_id)}&key={quote_plus(api_key)}"
        )
        try:
            payload = self.client.get_json(url)
            items = payload.get("items", [])
            if not items:
                return AssistantResponse(False, "No YouTube metadata found.", "youtube_metadata", data={"video_id": video_id})
            item = items[0]
            snippet = item.get("snippet", {})
            title = str(snippet.get("title", "Untitled"))
            channel = str(snippet.get("channelTitle", "unknown channel"))
            return AssistantResponse(
                True,
                f"YouTube video: {title} by {channel}",
                "youtube_metadata",
                data={"video_id": video_id, "title": title, "channel": channel, "provider": "youtube_data_api"},
            )
        except (KeyError, WebRequestError) as exc:
            return AssistantResponse(False, "YouTube metadata lookup failed.", "youtube_metadata", data={"error": str(exc)})

    def summarize_public_page(self, url: str) -> AssistantResponse:
        """Fetch and summarize a public HTTP(S) page without bypassing access controls."""
        cleaned = url.strip()
        parsed = urlparse(cleaned)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return AssistantResponse(False, "Provide a public http or https URL.", "page_summary")
        try:
            html = self.client.get_text(cleaned)
        except WebRequestError as exc:
            return AssistantResponse(
                False,
                "Public page fetch failed.",
                "page_summary",
                data={"url": cleaned, "error": str(exc)},
            )
        extractor = _TextExtractor()
        extractor.feed(html)
        text = " ".join(extractor.text_parts)
        title = " ".join(extractor.title_parts).strip() or parsed.netloc
        summary = text[:320].strip()
        if len(text) > 320:
            summary += "..."
        if not summary:
            return AssistantResponse(
                False,
                "No readable public text found on that page.",
                "page_summary",
                data={"url": cleaned},
            )
        return AssistantResponse(
            True,
            f"{title}: {summary}",
            "page_summary",
            data={"url": cleaned, "title": title, "summary": summary, "characters": len(text)},
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


def _extract_rss_titles(xml_text: str) -> list[str]:
    """Extract RSS titles without adding XML dependencies."""
    titles = []
    for match in re_findall(r"<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>", xml_text):
        title = next((part for part in match if part), "").strip()
        if title and not title.casefold().startswith("google news"):
            titles.append(_html_unescape(title))
    return titles


def _extract_youtube_video_id(value: str) -> str:
    """Extract a YouTube video id from a URL or return the id-like value."""
    parsed = urlparse(value)
    if parsed.netloc:
        if parsed.netloc.endswith("youtu.be"):
            return parsed.path.strip("/")
        if "youtube.com" in parsed.netloc:
            query = parse_qs(parsed.query)
            return query.get("v", [""])[0]
    if len(value) == 11 and all(char.isalnum() or char in {"_", "-"} for char in value):
        return value
    return ""


def _html_unescape(value: str) -> str:
    """Unescape the most common entities used in feed titles."""
    return (
        value.replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )


def re_findall(pattern: str, text: str) -> list[tuple[str, ...]]:
    """Local wrapper to keep regex import scoped to RSS parsing."""
    import re

    return re.findall(pattern, text, flags=re.IGNORECASE | re.DOTALL)
