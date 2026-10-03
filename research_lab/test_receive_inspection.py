"""PG-030 Receive / Inspection contract tests."""

from research_lab.receive_inspection import inspect_received_item


def _receipt():
    return {
        "status":"purchase_receipt_reconciled",
        "receipt_key":"receipt-030",
        "provider":"yahoo_shopping",
        "item_key":"item-030",
        "quantity":1,
        "actual_total_charged_jpy":2950,
        "capital_committed_jpy":2950,
        "reconciliation_passed":True,
        "capital_state":"awaiting_receipt_or_delivery",
        "provider_order_reference":"order-030",
    }


def main():
    ready=inspect_received_item(
        _receipt(),
        inspection_key="inspect-030",
        received_at="2026-10-03T05:00:00+00:00",
        inspected_at="2026-10-03T05:10:00+00:00",
        quantity_received=1,
        identity_verified=True,
        condition_grade="good",
        condition_matches_listing=True,
        damage_detected=False,
        missing_parts=False,
        counterfeit_suspected=False,
        functional_check_passed=True,
        return_window_open=True,
        note="received as expected",
    )
    assert ready["status"]=="inspection_complete"
    assert ready["disposition"]=="sale_ready"
    assert ready["sale_ready"] is True
    assert ready["return_required"] is False
    assert ready["capital_state"]=="inventory_ready_for_sale"
    assert ready["capital_basis_jpy"]==2950

    damaged=inspect_received_item(
        _receipt(),
        inspection_key="inspect-030-damaged",
        received_at="2026-10-03T05:00:00+00:00",
        inspected_at="2026-10-03T05:10:00+00:00",
        quantity_received=1,
        identity_verified=True,
        condition_grade="poor",
        condition_matches_listing=False,
        damage_detected=True,
        missing_parts=False,
        counterfeit_suspected=False,
        functional_check_passed=False,
        return_window_open=True,
        note="damaged",
    )
    assert damaged["disposition"]=="return_required"
    assert damaged["sale_ready"] is False
    assert damaged["return_required"] is True
    assert damaged["capital_state"]=="return_or_refund_pending"

    mismatch=inspect_received_item(
        _receipt(),
        inspection_key="inspect-030-mismatch",
        received_at="2026-10-03T05:00:00+00:00",
        inspected_at="2026-10-03T05:10:00+00:00",
        quantity_received=1,
        identity_verified=False,
        condition_grade="good",
        condition_matches_listing=True,
        damage_detected=False,
        missing_parts=False,
        counterfeit_suspected=False,
        functional_check_passed=True,
        return_window_open=False,
        note="identity mismatch outside return window",
    )
    assert mismatch["disposition"]=="inspection_hold"
    assert mismatch["requires_human_review"] is True

    print("PG-030 Receive / Inspection tests passed")


if __name__=="__main__":
    main()
