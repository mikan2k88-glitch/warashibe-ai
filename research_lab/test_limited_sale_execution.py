"""PG-033 Limited Sale Execution contract tests."""

from research_lab.limited_sale_execution import execute_limited_sale_listing


class FakeSaleAdapter:
    def __init__(self):
        self.calls=0

    def create_listing(self, payload):
        self.calls+=1
        return {
            "status":"listing_created",
            "listing_reference":"fake-listing-033",
            "listing_created":True,
            "network_call_attempted":True,
            "external_write_attempted":True,
            "listing_price_jpy":payload["approved_listing_price_jpy"],
        }


class FakeSaleExecutionRepository:
    def __init__(self):
        self.rows={}

    def get_by_idempotency_key(self,key):
        return self.rows.get(key)

    def append(self,row):
        self.rows[row["idempotency_key"]]=dict(row)
        return dict(row)


def _decision():
    return {
        "status":"human_sale_decision_recorded",
        "decision_key":"sale-decision-033",
        "plan_key":"sale-plan-033",
        "item_key":"item-033",
        "quantity":1,
        "marketplace":"mercari",
        "decision":"sell",
        "approved_listing_price_jpy":4100,
        "minimum_sale_price_jpy":3500,
        "max_marketplace_fee_jpy":450,
        "max_shipping_jpy":250,
        "decided_at":"2026-10-03T06:10:00+00:00",
        "valid_until":"2026-10-04T06:10:00+00:00",
        "execution_authorized_for_single_listing":True,
        "listing_created":False,
        "sale_completed":False,
    }


def main():
    repo=FakeSaleExecutionRepository()
    adapter=FakeSaleAdapter()

    result=execute_limited_sale_listing(
        decision=_decision(),
        adapter=adapter,
        execution_repository=repo,
        idempotency_key="sale-idem-033",
        now="2026-10-03T06:20:00+00:00",
        live_sale_execution_enabled=True,
        emergency_kill_switch_engaged=False,
    )
    assert result["status"]=="limited_sale_listing_created"
    assert result["listing_reference"]=="fake-listing-033"
    assert result["listing_price_jpy"]==4100
    assert result["execution_count"]==1
    assert result["idempotency_reused"] is False
    assert result["sale_completed"] is False
    assert adapter.calls==1

    repeated=execute_limited_sale_listing(
        decision=_decision(),
        adapter=adapter,
        execution_repository=repo,
        idempotency_key="sale-idem-033",
        now="2026-10-03T06:21:00+00:00",
        live_sale_execution_enabled=True,
        emergency_kill_switch_engaged=False,
    )
    assert repeated["idempotency_reused"] is True
    assert adapter.calls==1

    disabled=execute_limited_sale_listing(
        decision=_decision(),
        adapter=FakeSaleAdapter(),
        execution_repository=FakeSaleExecutionRepository(),
        idempotency_key="sale-idem-disabled",
        now="2026-10-03T06:20:00+00:00",
        live_sale_execution_enabled=False,
        emergency_kill_switch_engaged=False,
    )
    assert disabled["status"]=="limited_sale_blocked"
    assert disabled["reason"]=="live_sale_execution_disabled"

    killed=execute_limited_sale_listing(
        decision=_decision(),
        adapter=FakeSaleAdapter(),
        execution_repository=FakeSaleExecutionRepository(),
        idempotency_key="sale-idem-killed",
        now="2026-10-03T06:20:00+00:00",
        live_sale_execution_enabled=True,
        emergency_kill_switch_engaged=True,
    )
    assert killed["status"]=="limited_sale_blocked"
    assert killed["reason"]=="emergency_kill_switch_engaged"

    print("PG-033 Limited Sale Execution tests passed")


if __name__=="__main__":
    main()
