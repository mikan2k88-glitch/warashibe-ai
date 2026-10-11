from __future__ import annotations

from .listing_preview import build_listing_preview
from .outcome import build_outcome_record
from .sandbox_fulfillment import simulate_fulfillment
from .sandbox_order_flow import build_customer_order, build_supplier_order
from .sandbox_settlement_v53 import settle_sandbox_order


def run_v53_sandbox_cycle(
    promotion_review: dict,
    *,
    scenario: str = "delivered",
    quantity: int = 1,
) -> dict:
    if promotion_review.get("eligible_for_human_review") is not True:
        return {
            "status": "blocked",
            "reason": "promotion_review_not_ready",
            "live_execution_allowed": False,
        }

    listing = build_listing_preview(promotion_review)
    customer_order = build_customer_order(listing, quantity=quantity)
    supplier_order = build_supplier_order(customer_order, promotion_review)
    fulfillment = simulate_fulfillment(
        supplier_order,
        scenario=scenario,
        delivery_days=((promotion_review.get("review") or {}).get("candidate") or {}).get("delivery_days"),
    )
    settlement = settle_sandbox_order(
        customer_order,
        supplier_order,
        fulfillment,
        promotion_review,
    )

    candidate = (promotion_review.get("review") or {}).get("candidate") or {}
    outcome = build_outcome_record({
        "product_key": promotion_review.get("product_key"),
        "supplier": candidate.get("supplier"),
        "category": candidate.get("category"),
        "strategy": "promotion_review_v52",
        "mode": "sandbox_v53",
        "expected_net_profit": settlement.get("expected_net_profit"),
        "realized_net_profit": settlement.get("realized_net_profit"),
        "delivered": settlement.get("delivered"),
        "refunded": settlement.get("refunded"),
        "delivery_days": fulfillment.get("delivery_days") or 0,
    })

    completed = settlement["status"] in {
        "settled_sandbox",
        "refunded_sandbox",
        "cancelled_sandbox",
    }
    return {
        "version": "5.3",
        "status": "completed" if completed else "in_progress",
        "scenario": scenario,
        "listing_preview": listing,
        "customer_order": customer_order,
        "supplier_order": supplier_order,
        "fulfillment": fulfillment,
        "settlement": settlement,
        "outcome": outcome,
        "sandbox_cycle_complete": completed,
        "commerce_external_writes": False,
        "real_listing_created": False,
        "real_supplier_order_created": False,
        "real_payment_captured": False,
        "live_execution_allowed": False,
    }
