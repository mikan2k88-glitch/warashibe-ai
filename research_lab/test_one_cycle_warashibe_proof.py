"""PG-035 One-cycle Warashibe Proof contract tests."""

from research_lab.one_cycle_warashibe_proof import build_one_cycle_proof


def main():
    receipt={
        "status":"purchase_receipt_reconciled","receipt_key":"receipt-035","item_key":"item-035",
        "quantity":1,"actual_total_charged_jpy":2950,"capital_committed_jpy":2950,
        "reconciliation_passed":True,"capital_state":"awaiting_receipt_or_delivery",
    }
    inspection={
        "status":"inspection_complete","inspection_key":"inspect-035","receipt_key":"receipt-035",
        "item_key":"item-035","quantity":1,"sale_ready":True,"disposition":"sale_ready",
        "capital_basis_jpy":2950,"capital_state":"inventory_ready_for_sale",
    }
    plan={
        "status":"sale_plan_ready","plan_key":"plan-035","inspection_key":"inspect-035",
        "item_key":"item-035","quantity":1,"capital_basis_jpy":2950,
        "expected_sale_price_jpy":4000,"expected_net_proceeds_jpy":3390,
        "expected_profit_jpy":440,"estimated_days_to_sell":3,
        "expected_capital_velocity_jpy_per_day":146.67,
    }
    decision={
        "status":"human_sale_decision_recorded","decision_key":"decision-035",
        "plan_key":"plan-035","item_key":"item-035","quantity":1,"decision":"sell",
        "execution_authorized_for_single_listing":True,
    }
    listing={
        "status":"limited_sale_listing_created","idempotency_key":"sale-idem-035",
        "decision_key":"decision-035","plan_key":"plan-035","item_key":"item-035",
        "quantity":1,"listing_created":True,"sale_completed":False,
    }
    settlement={
        "status":"trade_settled","settlement_key":"settlement-035",
        "listing_idempotency_key":"sale-idem-035","plan_key":"plan-035","item_key":"item-035",
        "quantity":1,"starting_capital_jpy":3000,"capital_basis_jpy":2950,
        "uncommitted_cash_jpy":50,"actual_sale_price_jpy":4000,
        "actual_net_proceeds_jpy":3390,"trade_profit_jpy":440,
        "next_capital_jpy":3440,"capital_growth_jpy":440,
        "capital_growth_percent":14.67,"sale_completed":True,
        "settlement_recorded":True,"capital_state":"ready_for_next_candidate",
    }

    proof=build_one_cycle_proof(
        receipt=receipt,inspection=inspection,sale_plan=plan,
        sale_decision=decision,listing_execution=listing,settlement=settlement,
        proof_key="cycle-proof-035",
        cycle_started_at="2026-10-03T06:00:00+00:00",
        cycle_completed_at="2026-10-06T06:30:00+00:00",
        proof_mode="synthetic_auditable_cycle",
    )
    assert proof["status"]=="one_cycle_warashibe_proved"
    assert proof["chain_consistent"] is True
    assert proof["starting_capital_jpy"]==3000
    assert proof["next_capital_jpy"]==3440
    assert proof["capital_growth_jpy"]==440
    assert proof["capital_velocity_jpy_per_day"]==145.66
    assert proof["warashibe_loop_v2_contract_complete"] is True
    assert proof["live_external_actions_verified"] is False
    assert proof["ready_for_next_candidate"] is True

    print("PG-035 One-cycle Warashibe Proof tests passed")


if __name__=="__main__":
    main()
