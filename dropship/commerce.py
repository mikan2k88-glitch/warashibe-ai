from __future__ import annotations

from uuid import uuid4

from .ranking import rank_supplier_offers
from .sandbox import run_sandbox_cycle


def build_sandbox_commerce_plan(offers: list[dict]) -> dict:
    ranking = rank_supplier_offers(offers)
    best = ranking.get("best")
    if not best:
        return {
            "status": "blocked",
            "reason": "no_eligible_supplier_offer",
            "ranking": ranking,
            "external_writes": False,
            "live_execution_allowed": False,
        }

    offer = dict(best["offer"])
    payload = {
        **offer,
        **best["economics"],
        "platform_fee_rate": 0.0,
        "payment_fee_rate": 0.0,
        "ad_cost": best["economics"].get("ad_cost", 0.0),
        "expected_return_cost": best["economics"].get("expected_return_cost", 0.0),
        "refund_reserve": best["economics"].get("refund_reserve", 0.0),
        "supplier_allows_dropshipping": offer["supplier_allows_dropshipping"],
        "platform_terms_confirmed": offer["platform_terms_confirmed"],
        "supplier_reliable": offer["supplier_reliable"],
        "inventory_confirmed": offer["inventory_confirmed"],
    }
    cycle = run_sandbox_cycle(payload)
    commerce_key = f"sandbox-{offer['product_key']}-{uuid4().hex[:8]}"
    return {
        "status": cycle["status"],
        "commerce_key": commerce_key,
        "selected": best,
        "cycle": cycle,
        "customer_order": {
            "order_key": f"{commerce_key}:customer",
            "status": "simulated_received",
            "real_payment": False,
        },
        "supplier_order": {
            "order_key": f"{commerce_key}:supplier",
            "status": "simulated_ordered",
            "real_supplier_order": False,
            "automatic_retry_allowed": False,
        },
        "fulfillment": {
            "status": "simulated_delivered",
            "real_shipment": False,
        },
        "settlement": cycle.get("settlement") or {},
        "external_writes": False,
        "live_execution_allowed": False,
        "human_gate_required_for_live": True,
    }
