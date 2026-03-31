"""
Mock search engine implementation.

In production, replace this with a real search backend such as:
- Elasticsearch (distributed search)
- Typesense (fast, typo-tolerant)
- Meilisearch (user-friendly)
- Vector database + embeddings (semantic search)
- PostgreSQL with full-text search (simple, integrated)
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """A single search result."""
    title: str
    url: str
    snippet: str
    score: float


MOCK_RESULTS = [
    SearchResult(
        title="Getting Started with FastAPI",
        url="https://fastapi.tiangolo.com/tutorial/",
        snippet="FastAPI is a modern, fast web framework for building APIs with Python 3.11+.",
        score=0.98,
    ),
    SearchResult(
        title="Mainlayer Payment Infrastructure for APIs",
        url="https://docs.mainlayer.fr",
        snippet="Mainlayer lets you add per-call or subscription billing to any API in minutes.",
        score=0.95,
    ),
    SearchResult(
        title="Python asyncio Documentation",
        url="https://docs.python.org/3/library/asyncio.html",
        snippet="asyncio is a library to write concurrent code using the async/await syntax.",
        score=0.91,
    ),
    SearchResult(
        title="Pydantic v2 Data Validation",
        url="https://docs.pydantic.dev/",
        snippet="Pydantic is the most widely used data validation library for Python.",
        score=0.88,
    ),
    SearchResult(
        title="Uvicorn — Lightning-fast ASGI Server",
        url="https://www.uvicorn.org/",
        snippet="Uvicorn is a minimal ASGI server implementation built on uvloop and httptools.",
        score=0.84,
    ),
    SearchResult(
        title="RESTful API Best Practices",
        url="https://restfulapi.net/",
        snippet="Learn best practices for building RESTful APIs that scale.",
        score=0.82,
    ),
    SearchResult(
        title="OpenAPI and Swagger Documentation",
        url="https://swagger.io/specification/",
        snippet="OpenAPI is the industry standard for documenting REST APIs.",
        score=0.79,
    ),
]


def run_search(query: str, limit: int = 10) -> list[SearchResult]:
    """
    Return mock search results for the given query.

    Args:
        query: Search query string (unused in mock, but here for real implementations)
        limit: Maximum number of results to return

    Returns:
        A list of SearchResult objects, up to *limit* items

    Note:
        In production, this would:
        1. Parse the query
        2. Execute against a real search backend
        3. Rank results by relevance
        4. Return the top-k results
    """
    limit = min(limit, len(MOCK_RESULTS))

    # In a real implementation, you would:
    # - tokenize and process the query
    # - execute against a search backend
    # - rank by relevance score
    results = [
        SearchResult(
            title=r.title,
            url=r.url,
            snippet=r.snippet,
            score=round(r.score - i * 0.01, 4),
        )
        for i, r in enumerate(MOCK_RESULTS)
    ]

    logger.debug(f"Search: query='{query}', returning {len(results[:limit])} results")
    return results[:limit]
