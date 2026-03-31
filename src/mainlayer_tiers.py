"""
Tier and quota management via Mainlayer subscriptions.

Tiers:
  free   — 10 requests per day, no token required
  paid   — unlimited requests, requires a valid Mainlayer token

In production, replace the in-memory quota tracker with Redis or a database.
"""

import logging
import os
import time
from collections import defaultdict
from mainlayer import MainlayerClient

logger = logging.getLogger(__name__)

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
    """
    Verify that the provided token grants access to the resource.

    Args:
        resource_id: The resource identifier to check access for
        token: The Mainlayer payment token

    Returns:
        True if authorized, False otherwise

    Raises:
        Exception: If the verification request fails
    """
    client = get_client()
    try:
        access = await client.resources.verify_access(resource_id, token)
        logger.debug(f"Token verification: authorized={access.authorized}")
        return access.authorized
    except Exception as exc:
        logger.error(f"Token verification failed: {exc}")
        raise
