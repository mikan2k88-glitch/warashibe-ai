from __future__ import annotations

from .promotion_queue import build_promotion_queue
from .promotion_review_v52 import build_v52_promotion_review
from .real_product_ranking import rank_real_products
from .shadow_metrics import build_shadow_metrics


def _candidate(key: str, cost: float) -> dict:
    return {
        "product_key": key,
        "name": f"V52 Product {key}",
        "supplier": "proof-supplier",
        "category": "home",
        "supplier_cost": cost,
        "supplier_shipping": 0,
        "platform_fee_rate": 0.10,
        "payment_fee_rate": 0.035,
        "ad_cost": 0,
        "expected_return_cost": 0,
        "refund_reserve": 0,
        "delivery_days": 5,
        "inventory_confirmed": True,
        "supplier_allows_dropshipping": True,
        "platform_terms_confirmed": True,
        "supplier_reliable": True,
    }


def _quotes() -> list[dict]:
    return [
        {"price": 20, "currency": "USD", "seller_username": "seller-a"},
        {"price": 21, "currency": "USD", "seller_username": "seller-b"},
        {"price": 22, "currency": "USD", "seller_username": "seller-c"},
        {"price": 21.5, "currency": "USD", "seller_username": "seller-d"},
        {"price": 20.5, "currency": "USD", "seller_username": "seller-e"},
        {"price": 22.5, "currency": "USD", "seller_username": "seller-f"},
    ]


def _history(product_key: str) -> list[dict]:
    rows = []
    for day in range(1, 8):
        for index in range(3):
            rows.append({
                "product_key": product_key,
                "sale_price": 20 + (index * 0.5),
                "supplier_cost": 8.0 + (0.05 * index),
                "inventory_confirmed": True,
                "expected_net_profit": 5.0 + index,
                "observed_at": f"2026-10-{day:02d}T0{index}:00:00+00:00",
            })
    return rows


def build_v52_proof() -> dict:
    candidate = _candidate("v52-proof", 8)
    quotes = {"v52-proof": _quotes()}
    ranking = rank_real_products(
        [candidate],
        quotes,
        available_capital=3000,
        supplier_currency="USD",
        target_currency="USD",
    )
    best = ranking["best"]
    history = _history("v52-proof")
    metrics = build_shadow_metrics(history)["products"][0]
    review = build_v52_promotion_review(
        best,
        shadow_metrics=metrics,
        observations=history,
    )
    queue = build_promotion_queue([review])

    checks = {
        "real_product_ranked": ranking["eligible_count"] == 1,
        "single_item_rule": ranking["one_item_only"] is True,
        "shadow_depth_reached": metrics["observations"] >= 20 and metrics["observation_days"] >= 7,
        "evidence_mature": review["review"]["evidence_maturity"]["passed"] is True,
        "promotion_review_ready": review["eligible_for_human_review"] is True,
        "queue_ready": queue["ready_count"] == 1 and queue["next_review"] is not None,
        "human_gate_required": review["human_gate_required"] is True,
        "automatic_promotion_disabled": review["automatic_promotion"] is False,
        "commerce_write_not_performed": review["commerce_write_performed"] is False,
        "live_execution_disabled": review["live_execution_allowed"] is False,
    }

    return {
        "proof_version": "5.2",
        "passed": all(checks.values()),
        "checks": checks,
        "ranking": ranking,
        "review": review,
        "queue": queue,
        "maturity_ceiling": "promotion_review_human_gate",
        "live_execution_allowed": False,
    }


def build_v52_acceptance() -> dict:
    proof = build_v52_proof()
    checks = {
        "proof_passed": proof["passed"],
        "promotion_review_ready": proof["review"]["status"] == "promotion_review_ready",
        "next_review_available": proof["queue"]["next_review"] is not None,
        "human_gate_required": proof["review"]["human_gate_required"] is True,
        "automatic_promotion_disabled": proof["review"]["automatic_promotion"] is False,
        "live_execution_disabled": proof["live_execution_allowed"] is False,
    }
    return {
        "acceptance_version": "5.2",
        "passed": all(checks.values()),
        "checks": checks,
        "endpoint": "promotion_review_ready",
        "next_phase": "real_provider_shadow_evidence_and_human_review",
        "live_execution_allowed": False,
    }
