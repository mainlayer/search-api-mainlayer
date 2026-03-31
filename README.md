# search-api-mainlayer

[![CI](https://github.com/mainlayer/search-api-mainlayer/actions/workflows/ci.yml/badge.svg)](https://github.com/mainlayer/search-api-mainlayer/actions/workflows/ci.yml)

A FastAPI search service with **free and paid quota tiers** managed by [Mainlayer](https://mainlayer.fr).

## Features

- `GET /search?q=<query>` — full-text search with tiered access
- **Free tier**: 10 requests per day, no token needed, 3 results max
- **Paid tier**: unlimited requests, up to 50 results, requires Mainlayer payment token
- Quota tracking per IP address (in-memory; use Redis in production)
- Structured logging and error handling
- Production-ready response schemas

## 5-Minute Quickstart

### 1. Install dependencies

```bash
pip install -e ".[dev]"
```

### 2. Set environment variables

```bash
export MAINLAYER_API_KEY=your_mainlayer_api_key
export MAINLAYER_RESOURCE_ID=your_resource_id
export LOG_LEVEL=INFO
```

### 3. Start the server

```bash
uvicorn src.main:app --reload --port 8000
```

Server runs at `http://localhost:8000`

### 4. Test free-tier search

```bash
curl "http://localhost:8000/search?q=python"
```

Response:
```json
{
  "query": "python",
  "tier": "free",
  "results": [
    {
      "title": "Getting Started with FastAPI",
      "url": "https://fastapi.tiangolo.com/",
      "snippet": "FastAPI is a modern, fast framework...",
      "score": 0.98
    }
  ],
  "total": 1,
  "quota_remaining": 9
}
```

### 5. Test paid-tier search

```bash
curl -H "x-mainlayer-token: your_payment_token" \
  "http://localhost:8000/search?q=python&limit=50"
```

## API Reference

### `GET /search`

Search the index with optional pagination and tier selection.

**Query Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `q` | string | yes | — | Search query (1–500 characters) |
| `limit` | integer | no | 10 | Results to return (1–50; free tier capped at 3) |

**Headers:**

| Name | Description |
|------|-------------|
| `x-mainlayer-token` | Mainlayer payment token (enables paid tier; optional) |

**Response (200 OK):**

```json
{
  "query": "string",
  "tier": "free | paid",
  "results": [
    {
      "title": "string",
      "url": "string",
      "snippet": "string",
      "score": 0.0
    }
  ],
  "total": 0,
  "quota_remaining": 10
}
```

**Status Codes:**

- `200` — Search succeeded
- `402` — Payment required (invalid or missing token for paid tier)
- `429` — Free tier quota exhausted (10 requests per day)
- `422` — Invalid query parameter
- `500` — Server error

### `GET /health`

Health check endpoint.

```bash
curl http://localhost:8000/health
```

Response: `{"status": "ok", "version": "1.0.0"}`

## Pricing

- **Free tier**: $0/month, 10 requests/day, 3 results max, no signup required
- **Paid tier**: $9/month, unlimited requests, up to 50 results per query

Upgrade at [mainlayer.fr](https://mainlayer.fr)

## Architecture

### Quota Management

Free-tier quota is tracked in-memory per IP address with daily resets. For production:
- Replace `_quota` dict with Redis or a database
- Use user ID instead of IP for authenticated requests
- Implement distributed rate limiting

### Search Backend

The mock search engine (`src/search_engine.py`) returns static results. For production:
- Integrate with Elasticsearch, Typesense, Meilisearch, or PostgreSQL full-text search
- Add relevance ranking
- Implement caching

## Development

### Running tests

```bash
pytest tests/ -v
```

### Linting and type checking

```bash
mypy src/
black src/ tests/
```

### With Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .
COPY src/ src/
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Production Deployment

1. **Quota storage**: Replace in-memory dict with Redis or PostgreSQL
2. **Search backend**: Integrate real search engine (Elasticsearch, Meilisearch, etc.)
3. **Logging**: Configure centralized logging (e.g., ELK stack, Datadog)
4. **Monitoring**: Add Prometheus metrics for requests, latency, tier distribution
5. **Rate limiting**: Use a distributed rate limiter for the paid tier
6. **Security**: Add HTTPS, CORS, API key rotation

## Support

- Docs: https://docs.mainlayer.fr
- Issues: https://github.com/mainlayer/search-api-mainlayer/issues
