"""
Tier and quota management via Mainlayer subscriptions.

Tiers:
  free   — 10 requests per day, no token required
  paid   — unlimited requests, requires a valid Mainlayer token
"""

import os
import time
from collections import defaultdict
from mainlayer import MainlayerClient

FREE_DAILY_LIMIT = 10

_client: MainlayerClient | None = None

# In-memory quota tracker keyed by IP/identifier.
# In production, replace with Redis or a persistent store.
_quota: dict[str, dict] = defaultdict(lambda: {"count": 0, "reset_ts": 0.0})


def get_client() -> MainlayerClient:
    global _client
    if _client is None:
        _client = MainlayerClient(api_key=os.environ["MAINLAYER_API_KEY"])
    return _client


def _today_start() -> float:
    """Unix timestamp for the start of today (UTC midnight)."""
    now = time.time()
    return now - (now % 86_400)


def check_free_quota(identifier: str) -> tuple[bool, int]:
    """
    Check whether *identifier* (e.g. IP address) has free quota remaining.

    Returns:
        (allowed, remaining) — allowed is True if the request may proceed.
    """
    entry = _quota[identifier]
    today = _today_start()

    if entry["reset_ts"] < today:
        entry["count"] = 0
        entry["reset_ts"] = today

    remaining = FREE_DAILY_LIMIT - entry["count"]
    if remaining > 0:
        entry["count"] += 1
        return True, remaining - 1
    return False, 0


async def verify_paid_access(resource_id: str, token: str) -> bool:
    """Return True if *token* grants paid access to *resource_id*."""
    client = get_client()
    access = await client.resources.verify_access(resource_id, token)
    return access.authorized
