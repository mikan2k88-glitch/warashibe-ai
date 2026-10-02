"""PG-024 Live-readiness Audit contract tests."""

from research_lab.live_readiness_audit import evaluate_live_readiness


def _evidence():
    return {
        "identity_match_verified": True,
        "physical_policy_passed": True,
        "freshness_passed": True,
        "human_review_approved": True,
        "economics_viable": True,
        "preflight_ready": True,
        "pilot_session_ready": True,
        "purchase_intent_valid": True,
        "sandbox_adapter_verified": True,
        "sandbox_network_call_attempted": False,
        "sandbox_external_write_attempted": False,
        "duplicate_transaction_guard": True,
        "single_item_guard": True,
        "parallel_positions_disabled": True,
        "rls_enabled": True,
        "public_anon_write_policy_absent": True,
        "audit_cleanup_verified": True,
        "live_commerce_block_enabled": True,
        "rollback_plan_documented": True,
        "refund_cancel_path_documented": True,
        "marketplace_terms_review_required": True,
        "secrets_server_side_only": True,
    }


def main():
    result=evaluate_live_readiness(
        _evidence(),
        audit_key="pg024-audit-001",
        audited_at="2026-10-03T01:30:00+00:00",
        auditor_id="human",
    )
    assert result["status"]=="live_readiness_audit_complete"
    assert result["all_required_checks_passed"] is True
    assert result["ready_for_human_go_no_go"] is True
    assert result["human_go_no_go_required"] is True
    assert result["live_commerce_authorized"] is False
    assert result["execution_triggered"] is False
    assert result["commerce_authorized"] is False
    assert result["recommended_next_stage"]=="human_live_pilot_decision"

    bad=_evidence()
    bad["sandbox_network_call_attempted"]=True
    blocked=evaluate_live_readiness(
        bad,
        audit_key="pg024-audit-blocked",
        audited_at="2026-10-03T01:30:00+00:00",
        auditor_id="human",
    )
    assert blocked["all_required_checks_passed"] is False
    assert blocked["ready_for_human_go_no_go"] is False
    assert "sandbox_network_call_attempted" in blocked["failed_checks"]
    assert blocked["live_commerce_authorized"] is False

    print("PG-024 Live-readiness Audit tests passed")


if __name__=="__main__":
    main()
