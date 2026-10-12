from __future__ import annotations

from .discovery_keywords import generate_keywords


def build_discovery_plan(
    seed_candidates: list[dict],
    *,
    max_queries: int = 20,
    per_candidate_keywords: int = 3,
) -> dict:
    queries = []
    seen = set()
    for candidate in seed_candidates:
        for keyword in generate_keywords(candidate, max_keywords=per_candidate_keywords):
            normalized = keyword.strip()
            if not normalized or normalized.lower() in seen:
                continue
            seen.add(normalized.lower())
            queries.append({
                "query": normalized,
                "source_product_key": candidate.get("product_key"),
                "category": candidate.get("category"),
            })
            if len(queries) >= int(max_queries):
                break
        if len(queries) >= int(max_queries):
            break
    return {
        "status": "discovery_plan_ready",
        "query_count": len(queries),
        "queries": queries,
        "bounded": True,
        "live_execution_allowed": False,
    }
