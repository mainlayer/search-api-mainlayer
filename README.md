# search-api-mainlayer

[![CI](https://github.com/mainlayer/search-api-mainlayer/actions/workflows/ci.yml/badge.svg)](https://github.com/mainlayer/search-api-mainlayer/actions/workflows/ci.yml)

A FastAPI search service with **free and paid quota tiers** managed by [Mainlayer](https://mainlayer.fr).

## Features

- `GET /search?q=<query>` — full-text search with tiered access
- **Free tier**: 10 requests per day, no token needed, 3 results max
- **Paid tier**: unlimited requests, up to 50 results, requires Mainlayer token

## Quickstart

```bash
pip install mainlayer
```

```bash
export MAINLAYER_API_KEY=your_api_key
export MAINLAYER_RESOURCE_ID=your_resource_id
uvicorn src.main:app --reload
```

### Free-tier search

```python
import httpx

resp = httpx.get("http://localhost:8000/search", params={"q": "python async"})
data = resp.json()
print(f"Tier: {data['tier']}, quota remaining: {data['quota_remaining']}")
for r in data["results"]:
    print(r["title"], r["url"])
```

### Paid-tier search

```python
import httpx

resp = httpx.get(
    "http://localhost:8000/search",
    params={"q": "deep learning", "limit": 50},
    headers={"x-mainlayer-token": "<your-token>"},
)
data = resp.json()
```

## API Reference

### `GET /search`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | string | required | Search query (1–500 chars) |
| `limit` | int | 10 | Max results (1–50, free tier capped at 3) |

**Headers:** `x-mainlayer-token` (optional — enables paid tier)

**Response:**
```json
{
  "query": "python",
  "tier": "free",
  "results": [{ "title": "...", "url": "...", "snippet": "...", "score": 0.98 }],
  "total": 3,
  "quota_remaining": 9
}
```

## Payment

Upgrade to the paid tier at [mainlayer.fr](https://mainlayer.fr) for unlimited access.

## Development

```bash
pip install -e ".[dev]"
pytest tests/
```
