from atlas.core.orchestrator import AtlasOrchestrator
from atlas.modules.web_media import WebClient, WebMediaManager, WebRequestError


class StaticWebClient(WebClient):
    """Static web client for deterministic web integration tests."""

    def __init__(self, text: dict[str, str] | None = None, json_data: dict[str, dict] | None = None) -> None:
        self.text = text or {}
        self.json_data = json_data or {}

    def get_json(self, url: str) -> dict:
        if url not in self.json_data:
            raise WebRequestError(f"missing json fixture: {url}")
        return self.json_data[url]

    def get_text(self, url: str) -> str:
        if url not in self.text:
            raise WebRequestError(f"missing text fixture: {url}")
        return self.text[url]


def test_weather_validates_response_and_keeps_city() -> None:
    client = StaticWebClient(
        json_data={
            "https://wttr.in/delhi?format=j1": {
                "current_condition": [
                    {"temp_C": "31", "weatherDesc": [{"value": "Clear"}], "humidity": "50"}
                ]
            }
        },
    )
    response = WebMediaManager(client=client).weather("delhi")

    assert response.ok is True
    assert response.data["city"] == "delhi"
    assert "31C" in response.message


def test_weather_failure_still_returns_city() -> None:
    response = WebMediaManager(client=StaticWebClient()).weather("lahore")

    assert response.ok is False
    assert response.data["city"] == "lahore"


def test_news_parses_rss_items() -> None:
    client = StaticWebClient(
        text={
            "https://news.google.com/rss/search?q=linux": (
                "<rss><channel><item><title>One</title>"
                "<link>https://example.com/1</link></item></channel></rss>"
            )
        },
    )
    response = WebMediaManager(client=client).daily_news("linux")

    assert response.ok is True
    assert response.data["headlines"][0] == "One"


def test_youtube_without_key_returns_search_url() -> None:
    response = WebMediaManager(client=StaticWebClient()).youtube_metadata("atlas assistant")

    assert response.ok is True
    assert response.data["safe_path"] == "official_youtube_api_when_keyed"
    assert "youtube.com/results" in response.data["url"]


def test_page_summary_extracts_title_and_text() -> None:
    client = StaticWebClient(
        text={
            "https://example.com": (
                "<html><head><title>Example</title></head>"
                "<body><p>Hello world from Atlas.</p></body></html>"
            )
        },
    )
    response = WebMediaManager(client=client).summarize_public_page("https://example.com")

    assert response.ok is True
    assert response.data["title"] == "Example"
    assert "Hello world" in response.data["summary"]


def test_orchestrator_routes_milestone_5_commands() -> None:
    orchestrator = AtlasOrchestrator()

    assert orchestrator.execute_text("news linux").intent == "daily_news"
    assert orchestrator.execute_text("youtube atlas assistant").intent == "youtube_metadata"
    assert orchestrator.execute_text("summarize https://example.com").intent == "page_summary"
    assert orchestrator.execute_text("stock AAPL").intent == "stock_prices"
