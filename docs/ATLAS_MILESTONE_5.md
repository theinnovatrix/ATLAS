# Atlas Milestone 5

Milestone 5 adds safe web integrations. Atlas uses public endpoints, official
API upgrade slots, timeouts, retries, and response validation.

## Implemented now

- Weather lookup with retry and timeout handling.
- DuckDuckGo search URL generation.
- RSS-style news headline parsing.
- YouTube metadata lookup through the official Data API when `YOUTUBE_API_KEY`
  is set, with a safe search URL fallback when it is not.
- Public page summary extraction from title, description, and first paragraphs.
- Stock lookup URLs without requiring market-data credentials.
- Mocked tests for network success, parse failures, and fallback behavior.

## Try it

```bash
python -m atlas.cli "weather Delhi"
python -m atlas.cli "search linux voice assistant"
python -m atlas.cli "news technology"
python -m atlas.cli "youtube atlas assistant"
python -m atlas.cli "summarize https://example.com"
python -m atlas.cli "stock AAPL"
```

## Safety boundary

Atlas does not bypass login pages, private APIs, rate limits, or platform
protections. Social media integrations should use official APIs, OAuth, public
data, or user-authorized exports.

## Optional keys

- `YOUTUBE_API_KEY` enables official YouTube Data API metadata.
- Existing low-cost web/search upgrade slots remain available through
  environment variables documented in the README.
