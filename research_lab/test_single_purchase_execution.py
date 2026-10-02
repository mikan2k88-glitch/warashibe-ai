"""PG-028 Single Purchase Execution contract tests."""

from research_lab.single_purchase_execution import execute_single_purchase


class FakeLiveAdapter:
    def __init__(self):
        self.calls = 0

    def submit_order(self, validated_order):
        self.calls += 1
        return {
            "status": "live_order_submitted",
            "provider": validated_order["provider"],
            "order_reference": "fake-order-028",
            "order_created": True,
            "payment_created": True,
            "network_call_attempted": True,
            "external_write_attempted": True,
            "charged_amount_jpy": validated_order["total_cost_jpy"],
        }


class FakeExecutionRepository:
    def __init__(self):
        self.rows = {}

    def get_by_idempotency_key(self, key):
        return self.rows.get(key)

    def append(self, row):
        self.rows[row["idempotency_key"]] = dict(row)
        return dict(row)


def _validation():
    return {
        "status": "live_adapter_validation_ready",
        "validation_passed": True,
        "eligible_for_human_final_buy": True,
        "provider": "yahoo_shopping",
        "item_key": "item-028",
        "quantity": 1,
        "purchase_price_jpy": 2800,
        "total_cost_jpy": 2950,
        "approved_budget_jpy": 3000,
        "human_final_buy_required": True,
        "network_call_attempted": False,
        "external_write_attempted": False,
        "live_execution_authorized": False,
        "order_submission_authorized": False,
        "commerce_authorized": False,
    }


def _final_buy():
    return {
        "status": "human_final_buy_recorded",
        "decision": "buy",
        "confirmation_key": "final-buy-028",
        "provider": "yahoo_shopping",
        "item_key": "item-028",
        "quantity": 1,
        "max_total_cost_jpy": 3000,
        "confirmed_by": "human",
        "confirmed_at": "2026-10-03T03:30:00+00:00",
        "expires_at": "2026-10-03T03:45:00+00:00",
        "execution_authorized_for_single_order": True,
    }


def main():
    repo = FakeExecutionRepository()
    adapter = FakeLiveAdapter()

    result = execute_single_purchase(
        validation=_validation(),
        final_buy=_final_buy(),
        adapter=adapter,
        execution_repository=repo,
        idempotency_key="pg028-idem-001",
        now="2026-10-03T03:35:00+00:00",
        live_execution_enabled=True,
        emergency_kill_switch_engaged=False,
    )
    assert result["status"] == "single_purchase_executed"
    assert result["order_reference"] == "fake-order-028"
    assert result["charged_amount_jpy"] == 2950
    assert result["execution_count"] == 1
    assert result["idempotency_reused"] is False
    assert adapter.calls == 1

    repeated = execute_single_purchase(
        validation=_validation(),
        final_buy=_final_buy(),
        adapter=adapter,
        execution_repository=repo,
        idempotency_key="pg028-idem-001",
        now="2026-10-03T03:36:00+00:00",
        live_execution_enabled=True,
        emergency_kill_switch_engaged=False,
    )
    assert repeated["status"] == "single_purchase_executed"
    assert repeated["idempotency_reused"] is True
    assert adapter.calls == 1

    disabled = execute_single_purchase(
        validation=_validation(),
        final_buy=_final_buy(),
        adapter=FakeLiveAdapter(),
        execution_repository=FakeExecutionRepository(),
        idempotency_key="pg028-idem-disabled",
        now="2026-10-03T03:35:00+00:00",
        live_execution_enabled=False,
        emergency_kill_switch_engaged=False,
    )
    assert disabled["status"] == "single_purchase_blocked"
    assert disabled["reason"] == "live_execution_disabled"

    killed = execute_single_purchase(
        validation=_validation(),
        final_buy=_final_buy(),
        adapter=FakeLiveAdapter(),
        execution_repository=FakeExecutionRepository(),
        idempotency_key="pg028-idem-killed",
        now="2026-10-03T03:35:00+00:00",
        live_execution_enabled=True,
        emergency_kill_switch_engaged=True,
    )
    assert killed["status"] == "single_purchase_blocked"
    assert killed["reason"] == "emergency_kill_switch_engaged"

    print("PG-028 Single Purchase Execution tests passed")


if __name__ == "__main__":
    main()
