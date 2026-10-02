"""PG-017 approved review -> dry-run commerce plan contract tests."""

from datetime import datetime, timezone

from research_lab.dry_run_commerce_plan import build_dry_run_commerce_plan


def _record():
    return {
        "record_key": "pg017-record-001",
        "identity_key": "gtin:4901234567894:JPY",
        "proposal": {
            "status": "proposal_ready",
            "candidate_name": "Compact Item",
            "candidate_source": "rakuten_product",
            "candidate_purchase_price_jpy": 2800,
            "human_review_required": True,
            "commerce_authorized": False,
            "external_action_authorized": False,
            "purchase_authorized": False,
            "payment_authorized": False,
            "sale_authorized": False,
        },
        "observed_at": "2026-10-02T14:00:00+00:00",
        "captured_at": "2026-10-02T14:01:00+00:00",
        "commerce_authorized": False,
        "external_action_authorized": False,
    }


def _review(decision="approve"):
    return {
        "record_key": "pg017-record-001",
        "identity_key": "gtin:4901234567894:JPY",
        "decision": decision,
        "reviewer_id": "human",
        "reason": "reviewed",
        "reviewed_at": "2026-10-02T14:10:00+00:00",
        "commerce_authorized": False,
        "external_action_authorized": False,
        "purchase_authorized": False,
        "payment_authorized": False,
        "sale_authorized": False,
    }


def main():
    now = datetime(2026, 10, 2, 14, 15, tzinfo=timezone.utc)
    plan = build_dry_run_commerce_plan(
        _record(),
        _review(),
        plan_key="pg017-plan-001",
        generated_at=now.isoformat(),
    )

    assert plan["status"] == "dry_run_plan_ready"
    assert plan["source_record_key"] == "pg017-record-001"
    assert plan["identity_key"] == "gtin:4901234567894:JPY"
    assert plan["candidate_name"] == "Compact Item"
    assert plan["purchase_price_jpy"] == 2800
    assert plan["review_decision"] == "approve"
    assert plan["execution_mode"] == "dry_run"
    assert plan["execution_triggered"] is False
    assert plan["commerce_authorized"] is False
    assert plan["external_action_authorized"] is False
    assert plan["purchase_authorized"] is False
    assert plan["payment_authorized"] is False
    assert plan["sale_authorized"] is False

    try:
        build_dry_run_commerce_plan(
            _record(),
            _review("reject"),
            plan_key="pg017-plan-rejected",
            generated_at=now.isoformat(),
        )
    except ValueError as exc:
        assert "approved" in str(exc)
    else:
        raise AssertionError("rejected review must not produce a dry-run plan")

    print("PG-017 dry-run commerce plan tests passed")


if __name__ == "__main__":
    main()
