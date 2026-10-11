from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone


def _parse(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def summarize_operations(
    observations: list[dict],
    runs: list[dict],
    *,
    promotion_reviews: list[dict] | None = None,
) -> dict:
    by_product = defaultdict(list)
    for row in observations:
        by_product[str(row.get("product_key") or "unknown")].append(row)

    products = []
    for key, rows in by_product.items():
        days = {
            str(row.get("observed_at") or "")[:10]
            for row in rows
            if row.get("observed_at")
        }
        latest = max(
            rows,
            key=lambda row: _parse(row.get("observed_at")) or datetime.min.replace(tzinfo=timezone.utc),
        )
        products.append({
            "product_key": key,
            "observations": len(rows),
            "observation_days": len(days),
            "latest_observed_at": latest.get("observed_at"),
            "latest_opportunity_score": latest.get("opportunity_score"),
            "latest_expected_net_profit": latest.get("expected_net_profit"),
        })

    products.sort(key=lambda row: (-row["observation_days"], -row["observations"], row["product_key"]))

    sorted_runs = sorted(
        runs,
        key=lambda row: _parse(row.get("observed_at")) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    latest_run = sorted_runs[0] if sorted_runs else None

    reviews = list(promotion_reviews or [])
    ready_reviews = [
        row for row in reviews if row.get("eligible_for_human_review") is True
    ]

    return {
        "status": "operations_summary_ready",
        "observation_count": len(observations),
        "product_count": len(products),
        "run_count": len(runs),
        "latest_run": latest_run,
        "products": products,
        "promotion_review_count": len(reviews),
        "human_review_ready_count": len(ready_reviews),
        "human_review_ready_products": [
            row.get("product_key") for row in ready_reviews
        ],
        "live_execution_allowed": False,
    }
