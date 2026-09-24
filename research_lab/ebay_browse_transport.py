"""Read-only HTTP boundary for eBay Browse search.

OAuth token minting stays outside this module. The caller injects an Application
access token. Only GET item_summary/search is supported; no cart/order/offer
operations exist here.
"""

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

EBAY_BROWSE_SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
TRANSPORT_VERSION = "0.1"


def build_search_request(query, access_token, *, marketplace_id="EBAY_US", limit=20):
    query = str(query or "").strip()
    token = str(access_token or "").strip()
    if not query:
        raise ValueError("query is required")
    if not token:
        raise ValueError("application access token is required")
    limit = int(limit)
    if not 1 <= limit <= 200:
        raise ValueError("limit must be between 1 and 200")
    url = EBAY_BROWSE_SEARCH_URL + "?" + urlencode({"q": query, "limit": limit})
    return Request(url, method="GET", headers={
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": marketplace_id,
        "Accept": "application/json",
        "User-Agent": "warashibe-ai-research/0.1",
    })


def fetch_search_payload(query, access_token, *, marketplace_id="EBAY_US", limit=20, timeout=10):
    request = build_search_request(
        query, access_token, marketplace_id=marketplace_id, limit=limit
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("eBay response must be a JSON object")
    return payload
