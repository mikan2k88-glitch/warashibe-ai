"""Offline safety checks for the read-only eBay Browse transport boundary."""

from urllib.parse import parse_qs, urlparse

from research_lab.ebay_browse_transport import build_search_request


def main():
    request = build_search_request("camera & lens", "test-token", marketplace_id="EBAY_US", limit=20)
    parsed = urlparse(request.full_url)
    params = parse_qs(parsed.query)

    assert request.get_method() == "GET"
    assert parsed.scheme == "https"
    assert parsed.netloc == "api.ebay.com"
    assert parsed.path == "/buy/browse/v1/item_summary/search"
    assert params == {"q": ["camera & lens"], "limit": ["20"]}
    assert request.headers["Authorization"] == "Bearer test-token"
    assert request.headers["X-ebay-c-marketplace-id"] == "EBAY_US"

    for bad_query in ("", "   ", None):
        try:
            build_search_request(bad_query, "test-token")
        except ValueError:
            pass
        else:
            raise AssertionError("empty query must fail closed")

    for bad_token in ("", "   ", None):
        try:
            build_search_request("camera", bad_token)
        except ValueError:
            pass
        else:
            raise AssertionError("missing token must fail closed")

    for bad_limit in (0, 201):
        try:
            build_search_request("camera", "test-token", limit=bad_limit)
        except ValueError:
            pass
        else:
            raise AssertionError("out-of-range limit must fail closed")

    print("eBay Browse transport tests passed")


if __name__ == "__main__":
    main()
