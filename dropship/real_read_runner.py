from __future__ import annotations

from .market_cache import MarketQuoteCache
from .market_match import build_market_query
from .opportunity_pipeline import rank_opportunities
from .provider_normalizer import normalize_provider_row
from .source_budget import normalize_source_budget


def run_real_read_research(
    supplier_provider,
    market_provider,
    *,
    supplier_currency: str = "USD",
    target_currency: str | None = None,
    fx_rates: dict | None = None,
    budget: dict | None = None,
    cache: MarketQuoteCache | None = None,
) -> dict:
    limits = normalize_source_budget(budget)
    cache = cache or MarketQuoteCache()

    raw_candidates = supplier_provider.fetch_offers()
    candidates = [
        normalize_provider_row(
            row,
            provider_name=getattr(supplier_provider, "provider_name", "unknown"),
        )
        for row in raw_candidates[: limits["max_supplier_items"]]
        if isinstance(row, dict)
    ]

    quotes_by_product = {}
    query_count = 0
    cache_hits = 0
    errors = []

    for candidate in candidates:
        if query_count >= limits["max_market_queries"]:
            break
        key = str(candidate.get("product_key") or "")
        query = build_market_query(candidate)
        if not key or not query:
            continue

        quotes = cache.get(query)
        if quotes is not None:
            cache_hits += 1
        else:
            try:
                quotes = market_provider.search(query)
                query_count += 1
                cache.put(query, quotes)
            except Exception as exc:
                errors.append({
                    "product_key": key,
                    "query": query,
                    "error": str(exc),
                })
                quotes = []

        quotes_by_product[key] = list(quotes)[: limits["max_market_quotes_per_query"]]

    ranking = rank_opportunities(
        candidates,
        quotes_by_product,
        supplier_currency=supplier_currency,
        target_currency=target_currency,
        fx_rates=fx_rates,
    )

    return {
        "status": "completed" if candidates else "blocked",
        "supplier_provider": getattr(supplier_provider, "provider_name", "unknown"),
        "market_provider": getattr(market_provider, "provider_name", "unknown"),
        "budget": limits,
        "supplier_candidate_count": len(candidates),
        "market_query_count": query_count,
        "market_cache_hits": cache_hits,
        "market_cache": cache.stats(),
        "errors": errors,
        "quotes_by_product": quotes_by_product,
        "ranking": ranking,
        "commerce_external_writes": False,
        "live_execution_allowed": False,
    }
