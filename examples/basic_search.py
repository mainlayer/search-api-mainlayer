"""
Example: free-tier search (no token required, 10 req/day limit).

Usage:
    python examples/basic_search.py "python async"
"""

import sys
import httpx

API_BASE = "http://localhost:8000"
query = " ".join(sys.argv[1:]) or "machine learning"

resp = httpx.get(f"{API_BASE}/search", params={"q": query})

if resp.status_code == 429:
    print("Free quota exceeded — upgrade at https://mainlayer.fr")
    sys.exit(1)

resp.raise_for_status()
data = resp.json()

print(f"Tier: {data['tier']}  |  Quota remaining: {data.get('quota_remaining', 'N/A')}")
print(f"Results ({data['total']}):")
for r in data["results"]:
    print(f"  [{r['score']:.2f}] {r['title']}")
    print(f"         {r['url']}")
    print(f"         {r['snippet'][:80]}...")
    print()
