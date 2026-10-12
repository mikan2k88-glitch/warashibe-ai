from __future__ import annotations


def fetch_first_available(providers: list) -> dict:
    attempts = []
    for provider in providers:
        name = getattr(provider, "provider_name", "unknown")
        try:
            rows = provider.fetch_offers()
            attempts.append({
                "provider": name,
                "status": "ok",
                "count": len(rows),
            })
            return {
                "status": "ok",
                "provider": provider,
                "provider_name": name,
                "rows": rows,
                "attempts": attempts,
            }
        except Exception as exc:
            attempts.append({
                "provider": name,
                "status": "failed",
                "error": str(exc),
            })

    return {
        "status": "blocked",
        "provider": None,
        "provider_name": None,
        "rows": [],
        "attempts": attempts,
    }


def search_first_available_market(providers: list, query: str) -> dict:
    attempts = []
    for provider in providers:
        name = getattr(provider, "provider_name", "unknown")
        try:
            rows = provider.search(query)
            attempts.append({
                "provider": name,
                "status": "ok",
                "count": len(rows),
            })
            if rows:
                return {
                    "status": "ok",
                    "provider": provider,
                    "provider_name": name,
                    "quotes": rows,
                    "attempts": attempts,
                }
        except Exception as exc:
            attempts.append({
                "provider": name,
                "status": "failed",
                "error": str(exc),
            })

    return {
        "status": "blocked",
        "provider": None,
        "provider_name": None,
        "quotes": [],
        "attempts": attempts,
    }
