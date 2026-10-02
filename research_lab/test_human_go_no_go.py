"""PG-025 Human Go/No-Go Decision contract tests."""

from research_lab.human_go_no_go import build_human_go_no_go_decision


def _audit():
    return {
        "status":"live_readiness_audit_complete",
        "audit_key":"a025",
        "all_required_checks_passed":True,
        "ready_for_human_go_no_go":True,
        "human_go_no_go_required":True,
        "live_commerce_authorized":False,
        "execution_mode":"audit_only",
        "execution_triggered":False,
        "commerce_authorized":False,
        "external_action_authorized":False,
        "purchase_authorized":False,
        "payment_authorized":False,
        "sale_authorized":False,
    }


def main():
    go=build_human_go_no_go_decision(
        _audit(),
        decision_key="pg025-go-001",
        decision="go",
        decided_at="2026-10-03T02:00:00+00:00",
        reviewer_id="human",
        reason="limited pilot scope accepted",
        approved_budget_jpy=3000,
        max_transactions=1,
        approved_providers=["yahoo_shopping"],
        valid_until="2026-10-04T02:00:00+00:00",
    )
    assert go["status"]=="human_go_no_go_recorded"
    assert go["decision"]=="go"
    assert go["pilot_scope"]["approved_budget_jpy"]==3000
    assert go["pilot_scope"]["max_transactions"]==1
    assert go["pilot_scope"]["quantity_per_transaction"]==1
    assert go["pilot_scope"]["parallel_positions_allowed"] is False
    assert go["live_execution_authorized"] is False
    assert go["commerce_authorized"] is False

    nogo=build_human_go_no_go_decision(
        _audit(),
        decision_key="pg025-nogo-001",
        decision="no_go",
        decided_at="2026-10-03T02:00:00+00:00",
        reviewer_id="human",
        reason="not ready",
        approved_budget_jpy=0,
        max_transactions=0,
        approved_providers=[],
        valid_until="2026-10-04T02:00:00+00:00",
    )
    assert nogo["decision"]=="no_go"
    assert nogo["pilot_scope"]["approved_budget_jpy"]==0
    assert nogo["live_execution_authorized"] is False

    blocked=dict(_audit())
    blocked["ready_for_human_go_no_go"]=False
    try:
        build_human_go_no_go_decision(
            blocked,
            decision_key="pg025-invalid",
            decision="go",
            decided_at="2026-10-03T02:00:00+00:00",
            reviewer_id="human",
            reason="invalid",
            approved_budget_jpy=3000,
            max_transactions=1,
            approved_providers=["yahoo_shopping"],
            valid_until="2026-10-04T02:00:00+00:00",
        )
    except ValueError as exc:
        assert "ready_for_human_go_no_go" in str(exc)
    else:
        raise AssertionError("blocked audit must not allow GO")

    print("PG-025 Human Go/No-Go Decision tests passed")


if __name__=="__main__":
    main()
