from __future__ import annotations


PROHIBITED_AUTOMATIC_ACTIONS = {
    "create_live_listing",
    "submit_supplier_order",
    "capture_payment",
    "cancel_supplier_order",
    "issue_refund",
    "connect_live_broker_or_commerce_account",
}


READ_ONLY_ACTIONS = {
    "fetch_supplier_offers",
    "fetch_inventory",
    "fetch_tracking",
    "fetch_registry",
    "evaluate_candidate",
    "run_shadow",
}


def authorize_action(action: str, *, human_approved: bool = False) -> dict:
    if action in READ_ONLY_ACTIONS:
        return {
            "allowed": True,
            "mode": "read_only",
            "human_approval_required": False,
        }

    if action in PROHIBITED_AUTOMATIC_ACTIONS:
        return {
            "allowed": False,
            "mode": "blocked",
            "human_approval_required": True,
            "human_approved": bool(human_approved),
            "reason": "live commerce action is not enabled in this development stage",
        }

    return {
        "allowed": False,
        "mode": "blocked",
        "human_approval_required": True,
        "reason": "unknown action defaults to deny",
    }
