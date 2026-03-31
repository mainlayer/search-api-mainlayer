"""
Example: paid-tier search with a Mainlayer token (no rate limit).

Usage:
    MAINLAYER_TOKEN=<token> python examples/enterprise_search.py "deep learning"
"""

import os
import sys
import httpx

API_BASE = "http://localhost:8000"
TOKEN = os.getenv("MAINLAYER_TOKEN")

if not TOKEN:
    print("Error: set MAINLAYER_TOKEN environment variable")
    sys.exit(1)

query = " ".join(sys.argv[1:]) or "neural networks"

resp = httpx.get(
    f"{API_BASE}/search",
    params={"q": query, "limit": 50},
    headers={"x-mainlayer-token": TOKEN},
)

if resp.status_code == 402:
    print("Payment required — get access at https://mainlayer.fr")
    sys.exit(1)

resp.raise_for_status()
data = resp.json()

print(f"Tier: {data['tier']}  |  Total results: {data['total']}")
for r in data["results"]:
    print(f"  [{r['score']:.2f}] {r['title']}")
    print(f"         {r['url']}")
    print()
