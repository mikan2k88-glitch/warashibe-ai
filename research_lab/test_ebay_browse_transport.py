"""Offline safety checks for the read-only eBay Browse transport boundary."""

from urllib.parse import parse_qs, urlparse
from urllib.error import HTTPError
from unittest.mock import patch
from research_lab import ebay_browse_transport

from research_lab.ebay_browse_transport import build_search_request, fetch_search_payload, NoRedirectHandler


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

    for wrong_url in (
        "https://other.invalid/buy/browse/v1/item_summary/search",
        "http://api.ebay.com/buy/browse/v1/item_summary/search",
        "https://api.ebay.com/buy/browse/v1/order",
        "https://api.ebay.com.evil.invalid/buy/browse/v1/item_summary/search",
    ):
        with patch.object(ebay_browse_transport, "EBAY_BROWSE_SEARCH_URL", wrong_url):
            try:
                build_search_request("camera", "test-token")
            except ValueError:
                pass
            else:
                raise AssertionError("non-allowlisted destination accepted")

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

    # A redirect must never relay the bearer token to another host or path.
    handler = NoRedirectHandler()
    try:
        handler.redirect_request(request, None, 302, "redirect", {},
                                 "https://other.invalid/collect")
    except ValueError:
        pass
    else:
        raise AssertionError("redirect accepted")

    class FakeOpener:
        def __init__(self, error):
            self.error = error
            self.calls = []

        def open(self, req, timeout):
            self.calls.append((req.full_url, timeout))
            raise self.error

    for code in (403, 429):
        opener = FakeOpener(HTTPError(request.full_url, code, "blocked", {}, None))
        with patch("research_lab.ebay_browse_transport.build_opener", return_value=opener):
            try:
                fetch_search_payload("camera", "test-token")
            except HTTPError as exc:
                assert exc.code == code
            else:
                raise AssertionError("restriction was ignored")
        assert len(opener.calls) == 1  # no fallback, relay or retry

    print("eBay Browse transport tests passed")


if __name__ == "__main__":
    main()
