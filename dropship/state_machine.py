from __future__ import annotations

ALLOWED_TRANSITIONS = {
    "DISCOVERED": {"SUPPLIER_VERIFIED", "BLOCKED"},
    "SUPPLIER_VERIFIED": {"ECONOMICS_PASSED", "BLOCKED"},
    "ECONOMICS_PASSED": {"POLICY_PASSED", "BLOCKED"},
    "POLICY_PASSED": {"LISTED_SANDBOX", "BLOCKED"},
    "LISTED_SANDBOX": {"CUSTOMER_ORDER_RECEIVED", "LISTING_PAUSED"},
    "CUSTOMER_ORDER_RECEIVED": {"SUPPLIER_ORDERED_SANDBOX", "CUSTOMER_CANCELLED"},
    "SUPPLIER_ORDERED_SANDBOX": {"SHIPPED_SANDBOX", "ORDER_FAILED"},
    "SHIPPED_SANDBOX": {"DELIVERED_SANDBOX", "SHIPMENT_DELAYED"},
    "DELIVERED_SANDBOX": {"SETTLED_SANDBOX", "REFUND_REQUESTED"},
    "REFUND_REQUESTED": {"REFUNDED", "SETTLED_SANDBOX"},
}

TERMINAL_STATES = {
    "SETTLED_SANDBOX",
    "BLOCKED",
    "LISTING_PAUSED",
    "CUSTOMER_CANCELLED",
    "ORDER_FAILED",
    "REFUNDED",
}


def can_transition(current: str, target: str) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())


def transition(current: str, target: str) -> dict:
    allowed = can_transition(current, target)
    return {
        "from": current,
        "to": target,
        "allowed": allowed,
        "terminal": target in TERMINAL_STATES if allowed else current in TERMINAL_STATES,
    }
