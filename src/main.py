import logging
import os
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header, Query, Request
from pydantic import BaseModel, Field

from mainlayer import MainlayerClient
from src.mainlayer_tiers import check_free_quota, verify_paid_access
from src.search_engine import run_search, SearchResult

# Logging setup
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration
MAX_FREE_RESULTS = 3
MAX_PAID_RESULTS = 50
MAX_QUERY_LENGTH = 500


# Models
class SearchResultItem(BaseModel):
    title: str
    url: str
    snippet: str
    score: float = Field(..., ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    query: str
    tier: str
    results: list[SearchResultItem]
    total: int
    quota_remaining: Optional[int] = None


class ErrorResponse(BaseModel):
    detail: str
    error_code: str


# Lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Search API starting")
    yield
    logger.info("Search API shutting down")


# App setup
app = FastAPI(
    title="Search API",
    description="Tiered search API — free quota and paid tiers via Mainlayer",
    version="1.0.0",
    lifespan=lifespan,
)

ml = MainlayerClient(api_key=os.environ["MAINLAYER_API_KEY"])
RESOURCE_ID = os.environ["MAINLAYER_RESOURCE_ID"]


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/search", response_model=SearchResponse)
async def search(
    request: Request,
    q: str = Query(..., min_length=1, max_length=MAX_QUERY_LENGTH, description="Search query"),
    limit: int = Query(10, ge=1, le=MAX_PAID_RESULTS),
    x_mainlayer_token: Optional[str] = Header(None, description="Mainlayer payment token (paid tier)"),
):
    """
    Search across the index.

    - **q**: Search query (required, 1-500 chars)
    - **limit**: Number of results to return (1-50, default 10)
    - **x-mainlayer-token**: Payment token for paid tier (optional)

    Returns tier info, quota remaining (free tier), and results.
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Search request: query='{q[:30]}...', limit={limit}, tier={'paid' if x_mainlayer_token else 'free'}")

    # --- Paid tier ---
    if x_mainlayer_token:
        try:
            authorized = await verify_paid_access(RESOURCE_ID, x_mainlayer_token)
        except Exception as exc:
            logger.error(f"Payment verification failed: {exc}")
            raise HTTPException(
                status_code=402,
                detail="Payment verification failed. Ensure your token is valid.",
            )
        if not authorized:
            logger.warning(f"Unauthorized paid request from {client_ip}")
            raise HTTPException(
                status_code=402,
                detail="Payment required. Get access at mainlayer.fr",
            )
        try:
            results = run_search(q, limit=min(limit, MAX_PAID_RESULTS))
        except Exception as exc:
            logger.error(f"Search execution failed: {exc}")
            raise HTTPException(status_code=500, detail="Search failed. Please try again.")
        logger.info(f"Paid search: {len(results)} results for '{q}'")
        return SearchResponse(
            query=q,
            tier="paid",
            results=[SearchResultItem(**vars(r)) for r in results],
            total=len(results),
        )

    # --- Free tier ---
    allowed, remaining = check_free_quota(client_ip)
    if not allowed:
        logger.warning(f"Quota exhausted for {client_ip}")
        raise HTTPException(
            status_code=429,
            detail=(
                "Free tier limit reached (10 requests/day). "
                "Upgrade to paid at mainlayer.fr"
            ),
        )
    try:
        results = run_search(q, limit=min(limit, MAX_FREE_RESULTS))
    except Exception as exc:
        logger.error(f"Search execution failed: {exc}")
        raise HTTPException(status_code=500, detail="Search failed. Please try again.")

    logger.info(f"Free search: {len(results)} results, {remaining} quota remaining")
    return SearchResponse(
        query=q,
        tier="free",
        results=[SearchResultItem(**vars(r)) for r in results],
        total=len(results),
        quota_remaining=remaining,
    )
