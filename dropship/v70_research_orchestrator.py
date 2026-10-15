"""Warashibe v7.0: read-only research orchestration.

Uses bounded real provider reads when invoked by an operator. eBay Browse
asking prices are comparative signals, never a verified sale price.
Every unresolved evidence field blocks the economic promotion gate.
"""
from __future__ import annotations

from datetime import datetime, timezone
from math import isfinite
from .v611_evidence_mapping import assess_observed_candidate
from .cost_evidence_acquisition import acquire_cost_evidence

def _observed_at():
    return datetime.now(timezone.utc).isoformat()

def _known(value, source, timestamp):
    return {"status": "known", "value": value, "currency": "USD",
            "source": source, "observed_at": timestamp}

def research_v70(supplier_provider, market_provider, *, max_candidates=5,
                 max_market_queries=5, max_quotes=10, capital_usd=None,
                 freight_provider=None, max_freight_quotes=1):
    limits = (max_candidates, max_market_queries, max_quotes)
    if any(not isinstance(x, int) or not 1 <= x <= 20 for x in limits):
        raise ValueError("research_limits_must_be_between_1_and_20")
    if not isinstance(max_freight_quotes, int) or not 0 <= max_freight_quotes <= 20:
        raise ValueError('invalid_freight_quote_limit')
    timestamp = _observed_at()
    offers = supplier_provider.fetch_offers()[:max_candidates]
    report = []
    freight_attempts = 0
    market_cache = {}
    market_search_calls = 0
    for index, offer in enumerate(offers):
        if not isinstance(offer, dict):
            continue
        if freight_provider is not None and freight_attempts < max_freight_quotes:
            freight_attempts += 1
            offer = acquire_cost_evidence(offer, freight_provider=freight_provider,
                                          destination_country='US', quantity=1)['candidate']
        name = str(offer.get("name") or "")[:100]
        quote_rows = []
        error_kind = None
        # Deduplicate case-insensitive queries to reduce eBay API quota use.
        query = " ".join(name.casefold().split())
        if query in market_cache:
            quote_rows, error_kind = market_cache[query]
        elif query and market_search_calls < max_market_queries:
            market_search_calls += 1
            try:
                quote_rows = market_provider.search(name)[:max_quotes]
            except Exception as exc:
                error_kind = type(exc).__name__
            market_cache[query] = (quote_rows, error_kind)
        prices = sorted([
            float(q["price"]) for q in quote_rows
            if isinstance(q, dict) and q.get("currency") == "USD"
            and isinstance(q.get("price"), (float, int))
            and isfinite(q["price"]) and 0 < q["price"] < 100000
        ])
        market_median = ((prices[(len(prices)-1)//2] + prices[len(prices)//2]) / 2)
                         if prices else None
        evidence = {}
        cost = offer.get("supplier_cost")
        cost_status = (offer.get("cost_evidence") or {}).get("supplier_cost") or {}
        if (isinstance(cost, (float, int)) and not isinstance(cost, bool) and cost > 0
                and cost_status.get("status") == "known"):
            evidence["supplier_cost_usd"] = _known(cost, "cj_api", timestamp)
        shipping = (offer.get('cost_evidence') or {}).get('supplier_shipping') or {}
        freight_meta = (offer.get('metadata') or {}).get('shipping_evidence') or {}
        variant_price = freight_meta.get('variant_sell_price')
        if (freight_meta.get('status') == 'known'
                and freight_meta.get('variant_id')
                and freight_meta.get('variant_id') == shipping.get('variant_id')
                and freight_meta.get('currency') == 'USD'
                and freight_meta.get('variant_price_source') == 'cj-variant-query'
                and isinstance(variant_price, (int, float))
                and not isinstance(variant_price, bool) and 0 < variant_price < 100000):
            evidence['supplier_cost_usd'] = _known(variant_price, 'cj_api', timestamp)
        quoted = offer.get('supplier_shipping')
        if (shipping.get('status') == 'known' and shipping.get('currency') == 'USD'
                and shipping.get('variant_id') and shipping.get('destination_country') == 'US'
                and shipping.get('source') == 'cj-freight-calculate'
                and isinstance(quoted, (int, float)) and not isinstance(quoted, bool)
                and quoted >= 0):
            evidence['supplier_shipping_usd'] = _known(quoted, 'cj_api', timestamp)
        # Freight must be independently quoted for the exact variant, region and quantity.
        # Never turn a legacy zero shipping placeholder into a known value.
        observation = {"candidate_id": str(offer.get("product_key") or ""),
                       "evidence": evidence}
        assessed = assess_observed_candidate(observation, capital_usd=capital_usd)
        report.append({
            "candidate_id": observation["candidate_id"],
            "name": name,
            "market_quote_count": len(prices),
            "indicative_ask_median_usd": market_median,
            "market_error_kind": error_kind,
            "assessment": assessed,
            "unknown_fields": assessed["unknown_fields"],
            "live_execution_allowed": False,
        })
    # Missing evidence is prioritized; quote medians never count as proven profit.
    report.sort(key=lambda row: (len(row["unknown_fields"]),
                                  -(row["market_quote_count"]),
                                  row["candidate_id"]))
    selected = report[0] if report else None
    return {
        "version": "7.0",
        "mode": "read_only_research",
        "research_components_implemented": {
            "v6.12_source_collection": True,
            "v6.13_fee_return_gap_report": True,
            "v6.14_fail_closed_economics": True,
            "v6.15_bounded_candidate_ranking": True,
            "v6.16_human_gate_package": True,
            "v6.17_shadow_observation": True,
            "v7.0_research_orchestrator": True,
        },
        "observed_at": timestamp,
        "candidate_count": len(report),
        "freight_quote_attempts": freight_attempts,
        "market_search_calls": market_search_calls,
        "candidates": report,
        "proposed_single_candidate": selected,
        "next_evidence_actions": selected["assessment"]["next_evidence_actions"] if selected else [],
        "evidence_ready": False,
        "acceptance_status": "pending_actual_data_and_shadow_validation",
        "shadow_observation_only": True,
        "external_commerce_write": False,
        "human_gate_required": True,
        "human_gate_ready": False,
        "live_execution_allowed": False,
    }
