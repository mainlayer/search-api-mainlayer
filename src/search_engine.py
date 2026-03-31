"""
Mock search engine.

Replace `run_search` with a real search backend (e.g. Elasticsearch,
Typesense, Meilisearch, or a vector DB) for production use.
"""

from dataclasses import dataclass


@dataclass
class SearchResult:
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
]


def run_search(query: str, limit: int = 10) -> list[SearchResult]:
    """
    Return mock search results for *query*, up to *limit* items.

    In production, replace this with a real search engine call.
    """
    results = [
        SearchResult(
            title=r.title,
            url=r.url,
            snippet=r.snippet,
            score=round(r.score - i * 0.01, 4),
        )
        for i, r in enumerate(MOCK_RESULTS)
    ]
    return results[:limit]
