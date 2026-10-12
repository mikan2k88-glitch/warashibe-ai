from __future__ import annotations


def build_listing_preview(review: dict) -> dict:
    candidate = (review.get("review") or {}).get("candidate") or {}
    summary = review.get("summary") or {}
    ready = review.get("eligible_for_human_review") is True

    return {
        "status": "listing_preview_ready" if ready else "blocked",
        "product_key": review.get("product_key"),
        "title": candidate.get("name"),
        "price": candidate.get("sale_price"),
        "currency": candidate.get("pricing_currency") or "USD",
        "supplier": candidate.get("supplier"),
        "delivery_days": candidate.get("delivery_days"),
        "expected_net_profit": summary.get("expected_net_profit"),
        "margin_percent": summary.get("margin_percent"),
        "required_working_capital": summary.get("required_working_capital"),
        "preview_only": True,
        "real_listing_created": False,
        "external_write_performed": False,
        "live_execution_allowed": False,
    }
