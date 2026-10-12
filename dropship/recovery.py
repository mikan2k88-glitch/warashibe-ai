from __future__ import annotations


RETRYABLE_READ_ACTIONS = {
    "fetch_supplier_offers",
    "fetch_inventory",
    "fetch_tracking",
    "fetch_registry",
}

HARD_BLOCK_ACTIONS = {
    "create_live_listing",
    "submit_supplier_order",
    "capture_payment",
    "cancel_supplier_order",
    "issue_refund",
}


def classify_recovery(action: str, error_kind: str, attempts: int = 0, max_attempts: int = 3) -> dict:
    if action in HARD_BLOCK_ACTIONS:
        return {
            "action": action,
            "classification": "hard_block",
            "retry_allowed": False,
            "reason": "live write action must never be automatically retried",
        }

    transient = error_kind in {"timeout", "connection", "http_429", "http_5xx"}
    retry_allowed = action in RETRYABLE_READ_ACTIONS and transient and attempts < max_attempts
    return {
        "action": action,
        "classification": "transient_read" if retry_allowed else "manual_review",
        "retry_allowed": retry_allowed,
        "attempts": attempts,
        "max_attempts": max_attempts,
    }
