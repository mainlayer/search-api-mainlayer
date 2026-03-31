import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Query, Request
from pydantic import BaseModel
from mainlayer import MainlayerClient
from src.mainlayer_tiers import check_free_quota, verify_paid_access
from src.search_engine import run_search, SearchResult

app = FastAPI(
    title="Search API",
    description="Tiered search API — free quota and paid tiers via Mainlayer",
    version="1.0.0",
)

ml = MainlayerClient(api_key=os.environ["MAINLAYER_API_KEY"])
RESOURCE_ID = os.environ["MAINLAYER_RESOURCE_ID"]

MAX_FREE_RESULTS = 3
MAX_PAID_RESULTS = 50


class SearchResultItem(BaseModel):
    title: str
    url: str
    snippet: str
    score: float


class SearchResponse(BaseModel):
    query: str
    tier: str
    results: list[SearchResultItem]
    total: int
    quota_remaining: Optional[int] = None


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/search", response_model=SearchResponse)
async def search(
    request: Request,
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    limit: int = Query(10, ge=1, le=MAX_PAID_RESULTS),
    x_mainlayer_token: Optional[str] = Header(None, description="Mainlayer payment token (paid tier)"),
):
    client_ip = request.client.host if request.client else "unknown"

    # --- Paid tier ---
    if x_mainlayer_token:
        authorized = await verify_paid_access(RESOURCE_ID, x_mainlayer_token)
        if not authorized:
            raise HTTPException(
                status_code=402,
                detail="Payment required. Get access at mainlayer.fr",
            )
        results = run_search(q, limit=min(limit, MAX_PAID_RESULTS))
        return SearchResponse(
            query=q,
            tier="paid",
            results=[SearchResultItem(**vars(r)) for r in results],
            total=len(results),
        )

    # --- Free tier ---
    allowed, remaining = check_free_quota(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=(
                "Free tier limit reached (10 requests/day). "
                "Upgrade to paid at mainlayer.fr"
            ),
        )
    results = run_search(q, limit=min(limit, MAX_FREE_RESULTS))
    return SearchResponse(
        query=q,
        tier="free",
        results=[SearchResultItem(**vars(r)) for r in results],
        total=len(results),
        quota_remaining=remaining,
    )
