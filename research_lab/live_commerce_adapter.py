"""PG-027 Live Commerce Adapter Interface.

Defines the common contract for future live-commerce adapters while keeping
all external execution disabled until the PG-028 Human Gate is explicitly
crossed. No method in DisabledLiveCommerceAdapter performs a network call.
"""

from abc import ABC, abstractmethod

ADAPTER_VERSION = "0.1"


def _money(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{name} must be a non-negative number")
    return int(round(value))


def _text(value, name, max_length=300):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")
    value = value.strip()
    if len(value) > max_length:
        raise ValueError(f"{name} is too long")
    return value


class LiveCommerceAdapterInterface(ABC):
    @abstractmethod
    def prepare_order(self, guard, *, item_key, purchase_price_jpy, total_cost_jpy):
        raise NotImplementedError

    @abstractmethod
    def validate_order(self, prepared_order):
        raise NotImplementedError

    @abstractmethod
    def submit_order(self, validated_order):
        raise NotImplementedError

    @abstractmethod
    def get_order_status(self, order_reference):
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_reference):
        raise NotImplementedError


class DisabledLiveCommerceAdapter(LiveCommerceAdapterInterface):
    """Live-shaped adapter with execution deliberately disabled."""

    mode = "live_interface_disabled"

    def __init__(self, *, provider):
        self.provider = _text(provider, "provider", 100)

    @staticmethod
    def _validate_guard(guard):
        if not isinstance(guard, dict):
            raise ValueError("guard must be a dictionary")
        if guard.get("status") != "live_pilot_guard_passed":
            raise ValueError("live_pilot_guard_passed required")
        if guard.get("guard_passed") is not True:
            raise ValueError("guard_passed=True required")
        if guard.get("eligible_for_live_adapter_validation") is not True:
            raise ValueError("adapter validation eligibility required")
        if guard.get("quantity") != 1:
            raise ValueError("exactly one item required")
        if guard.get("human_final_buy_required") is not True:
            raise ValueError("human final buy must remain required")
        if guard.get("live_execution_authorized") is not False:
            raise ValueError("live execution must remain unauthorized")
        if guard.get("commerce_authorized") is not False:
            raise ValueError("commerce must remain unauthorized")
        return guard

    def prepare_order(self, guard, *, item_key, purchase_price_jpy, total_cost_jpy):
        guard = self._validate_guard(guard)
        if guard.get("provider") != self.provider:
            raise ValueError("provider mismatch")
        purchase_price = _money(purchase_price_jpy, "purchase_price_jpy")
        total_cost = _money(total_cost_jpy, "total_cost_jpy")
        approved_budget = _money(guard.get("approved_budget_jpy"), "approved_budget_jpy")
        if total_cost > approved_budget:
            raise ValueError("total cost exceeds approved budget")
        if purchase_price > total_cost:
            raise ValueError("purchase price must not exceed total cost")

        return {
            "version": ADAPTER_VERSION,
            "status": "live_adapter_order_prepared",
            "adapter_mode": self.mode,
            "provider": self.provider,
            "item_key": _text(item_key, "item_key", 200),
            "quantity": 1,
            "purchase_price_jpy": purchase_price,
            "total_cost_jpy": total_cost,
            "approved_budget_jpy": approved_budget,
            "human_final_buy_required": True,
            "network_call_attempted": False,
            "external_write_attempted": False,
            "live_execution_authorized": False,
            "order_submission_authorized": False,
            "commerce_authorized": False,
            "execution_triggered": False,
        }

    def validate_order(self, prepared_order):
        if not isinstance(prepared_order, dict):
            raise ValueError("prepared_order must be a dictionary")
        if prepared_order.get("status") != "live_adapter_order_prepared":
            raise ValueError("live_adapter_order_prepared required")
        if prepared_order.get("provider") != self.provider:
            raise ValueError("provider mismatch")
        if prepared_order.get("quantity") != 1:
            raise ValueError("exactly one item required")
        if prepared_order.get("human_final_buy_required") is not True:
            raise ValueError("human final buy must remain required")
        if prepared_order.get("network_call_attempted") is not False:
            raise ValueError("network calls must not have occurred")
        if prepared_order.get("external_write_attempted") is not False:
            raise ValueError("external writes must not have occurred")
        if prepared_order.get("live_execution_authorized") is not False:
            raise ValueError("live execution must remain unauthorized")

        return {
            **prepared_order,
            "status": "live_adapter_validation_ready",
            "validation_passed": True,
            "eligible_for_human_final_buy": True,
            "order_submission_authorized": False,
            "network_call_attempted": False,
            "external_write_attempted": False,
            "live_execution_authorized": False,
            "commerce_authorized": False,
            "execution_triggered": False,
        }

    def _blocked(self, action, *, order_reference=None):
        return {
            "version": ADAPTER_VERSION,
            "status": "live_adapter_blocked",
            "adapter_mode": self.mode,
            "provider": self.provider,
            "requested_action": action,
            "order_reference": order_reference,
            "reason": "human_gate_before_pg028",
            "network_call_attempted": False,
            "external_write_attempted": False,
            "order_created": False,
            "payment_created": False,
            "sale_created": False,
            "live_execution_authorized": False,
            "order_submission_authorized": False,
            "execution_triggered": False,
            "commerce_authorized": False,
            "external_action_authorized": False,
            "purchase_authorized": False,
            "payment_authorized": False,
            "sale_authorized": False,
        }

    def submit_order(self, validated_order):
        if not isinstance(validated_order, dict):
            raise ValueError("validated_order must be a dictionary")
        if validated_order.get("status") != "live_adapter_validation_ready":
            raise ValueError("live_adapter_validation_ready required")
        if validated_order.get("validation_passed") is not True:
            raise ValueError("validated order required")
        if validated_order.get("eligible_for_human_final_buy") is not True:
            raise ValueError("human final buy eligibility required")
        return self._blocked("submit_order")

    def get_order_status(self, order_reference):
        return self._blocked(
            "get_order_status",
            order_reference=_text(order_reference, "order_reference", 200),
        )

    def cancel_order(self, order_reference):
        return self._blocked(
            "cancel_order",
            order_reference=_text(order_reference, "order_reference", 200),
        )
