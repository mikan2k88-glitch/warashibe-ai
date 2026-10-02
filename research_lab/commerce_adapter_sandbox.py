"""PG-023 Commerce Adapter Sandbox.

This adapter is deliberately incapable of live commerce. Every action is a local
no-op audit result: no marketplace write, order, payment, listing, or sale call.
"""

SANDBOX_VERSION = "0.1"


def _validate_intent(intent):
    if not isinstance(intent, dict):
        raise ValueError("intent must be a dictionary")
    if intent.get("status") != "purchase_intent_recorded":
        raise ValueError("purchase_intent_recorded intent required")
    if intent.get("intent_type") != "human_purchase_intent":
        raise ValueError("human_purchase_intent required")
    if intent.get("quantity") != 1:
        raise ValueError("sandbox requires exactly one item")
    if intent.get("order_submission_authorized") is not False:
        raise ValueError("live order submission must remain blocked")
    for key in (
        "commerce_authorized",
        "external_action_authorized",
        "purchase_authorized",
        "payment_authorized",
        "sale_authorized",
    ):
        if intent.get(key) is not False:
            raise ValueError(f"{key} must remain false")
    return intent


def _provider(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("marketplace is required")
    return value.strip()


class SandboxCommerceAdapter:
    mode = "sandbox_noop"

    def _result(self, intent, *, marketplace, action):
        intent = _validate_intent(intent)
        provider = _provider(marketplace)
        return {
            "version": SANDBOX_VERSION,
            "status": "sandbox_blocked",
            "adapter_mode": self.mode,
            "requested_action": action,
            "provider": provider,
            "intent_key": intent.get("intent_key"),
            "session_key": intent.get("session_key"),
            "record_key": intent.get("record_key"),
            "plan_key": intent.get("plan_key"),
            "identity_key": intent.get("identity_key"),
            "quantity": 1,
            "network_call_attempted": False,
            "external_write_attempted": False,
            "order_created": False,
            "payment_created": False,
            "listing_created": False,
            "sale_created": False,
            "execution_triggered": False,
            "commerce_authorized": False,
            "external_action_authorized": False,
            "purchase_authorized": False,
            "payment_authorized": False,
            "sale_authorized": False,
            "reason": "live_commerce_disabled",
        }

    def submit_purchase(self, intent, *, marketplace):
        return self._result(intent, marketplace=marketplace, action="submit_purchase")

    def submit_sale(self, intent, *, marketplace):
        return self._result(intent, marketplace=marketplace, action="submit_sale")
