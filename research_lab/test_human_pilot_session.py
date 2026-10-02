"""PG-021 Human Pilot Session contract tests."""

from research_lab.human_pilot_session import build_human_pilot_session


def _preflight():
    return {
        "status":"preflight_ready",
        "record_key":"r021",
        "plan_key":"p021",
        "identity_key":"gtin:4901234567894:JPY",
        "required_cash_jpy":3000,
        "available_capital_jpy":3000,
        "quantity":1,
        "capital_commitment_mode":"single_item",
        "parallel_positions_allowed":False,
        "ready_for_human_purchase_confirmation":True,
        "human_final_confirmation_required":True,
        "execution_mode":"dry_run",
        "execution_triggered":False,
        "commerce_authorized":False,
        "external_action_authorized":False,
        "purchase_authorized":False,
        "payment_authorized":False,
        "sale_authorized":False,
    }


def main():
    session=build_human_pilot_session(
        _preflight(),
        session_key="pg021-session-001",
        started_at="2026-10-03T00:30:00+00:00",
        operator_id="human",
        note="pilot review",
    )
    assert session["status"]=="pilot_session_ready"
    assert session["session_state"]=="awaiting_human_final_confirmation"
    assert session["record_key"]=="r021"
    assert session["plan_key"]=="p021"
    assert session["identity_key"]=="gtin:4901234567894:JPY"
    assert session["required_cash_jpy"]==3000
    assert session["quantity"]==1
    assert session["parallel_positions_allowed"] is False
    assert session["human_final_confirmation_required"] is True
    assert session["execution_triggered"] is False
    assert session["commerce_authorized"] is False

    blocked=dict(_preflight())
    blocked["status"]="preflight_blocked"
    blocked["ready_for_human_purchase_confirmation"]=False
    try:
        build_human_pilot_session(
            blocked,
            session_key="pg021-session-blocked",
            started_at="2026-10-03T00:30:00+00:00",
            operator_id="human",
            note="blocked",
        )
    except ValueError as exc:
        assert "preflight_ready" in str(exc)
    else:
        raise AssertionError("blocked preflight must not create a pilot session")

    print("PG-021 Human Pilot Session tests passed")


if __name__=="__main__":
    main()
