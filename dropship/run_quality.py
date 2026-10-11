from __future__ import annotations


def assess_run_quality(result: dict) -> dict:
    candidate_count = int(result.get("supplier_candidate_count") or 0)
    query_count = int(result.get("market_query_count") or 0)
    errors = list(result.get("errors") or [])
    ranked_count = int((result.get("ranking") or {}).get("evaluated_count") or 0)
    market_covered = len(result.get("quotes_by_product") or {})

    checks = {
        "supplier_candidates_present": candidate_count > 0,
        "market_queries_completed": query_count > 0,
        "market_coverage_present": market_covered > 0,
        "ranked_opportunities_present": ranked_count > 0,
        "error_ratio_ok": len(errors) <= max(1, candidate_count // 2),
    }
    passed = all(checks.values())
    return {
        "status": "run_quality_passed" if passed else "run_quality_degraded",
        "passed": passed,
        "checks": checks,
        "candidate_count": candidate_count,
        "query_count": query_count,
        "market_covered_products": market_covered,
        "ranked_opportunities": ranked_count,
        "error_count": len(errors),
        "live_execution_allowed": False,
    }
