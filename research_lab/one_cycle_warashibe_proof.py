"""PG-035 One-cycle Warashibe Proof.

Verifies that one item's audited artifacts form a consistent chain from
purchase receipt through settlement and capital handoff. Synthetic proof is
kept explicitly distinct from verified external live commerce.
"""

from datetime import datetime, timezone

PROOF_VERSION="0.1"


def _text(value,name,max_length=300):
    if not isinstance(value,str) or not value.strip():
        raise ValueError(f"{name} is required")
    value=value.strip()
    if len(value)>max_length:
        raise ValueError(f"{name} is too long")
    return value


def _utc(value,name):
    value=_text(value,name,80)
    text=value[:-1]+"+00:00" if value.endswith("Z") else value
    dt=datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def build_one_cycle_proof(
    *,
    receipt,
    inspection,
    sale_plan,
    sale_decision,
    listing_execution,
    settlement,
    proof_key,
    cycle_started_at,
    cycle_completed_at,
    proof_mode,
):
    artifacts=[receipt,inspection,sale_plan,sale_decision,listing_execution,settlement]
    if not all(isinstance(x,dict) for x in artifacts):
        raise ValueError("all artifacts must be dictionaries")

    expected_statuses=[
        (receipt,"purchase_receipt_reconciled"),
        (inspection,"inspection_complete"),
        (sale_plan,"sale_plan_ready"),
        (sale_decision,"human_sale_decision_recorded"),
        (listing_execution,"limited_sale_listing_created"),
        (settlement,"trade_settled"),
    ]
    for artifact,status in expected_statuses:
        if artifact.get("status")!=status:
            raise ValueError(f"{status} required")

    item=receipt.get("item_key")
    chain_checks={
        "receipt_to_inspection": inspection.get("receipt_key")==receipt.get("receipt_key"),
        "same_item": all(x.get("item_key")==item for x in artifacts),
        "inspection_to_plan": sale_plan.get("inspection_key")==inspection.get("inspection_key"),
        "plan_to_decision": sale_decision.get("plan_key")==sale_plan.get("plan_key"),
        "decision_to_listing": listing_execution.get("decision_key")==sale_decision.get("decision_key"),
        "plan_to_listing": listing_execution.get("plan_key")==sale_plan.get("plan_key"),
        "listing_to_settlement": settlement.get("listing_idempotency_key")==listing_execution.get("idempotency_key"),
        "plan_to_settlement": settlement.get("plan_key")==sale_plan.get("plan_key"),
        "quantity_one": all(x.get("quantity")==1 for x in artifacts),
        "receipt_reconciled": receipt.get("reconciliation_passed") is True,
        "sale_ready": inspection.get("sale_ready") is True and inspection.get("disposition")=="sale_ready",
        "human_sell": sale_decision.get("decision")=="sell",
        "single_listing_authorized": sale_decision.get("execution_authorized_for_single_listing") is True,
        "listing_created": listing_execution.get("listing_created") is True,
        "sale_completed": settlement.get("sale_completed") is True,
        "settlement_recorded": settlement.get("settlement_recorded") is True,
        "next_candidate_ready": settlement.get("capital_state")=="ready_for_next_candidate",
    }
    chain_consistent=all(chain_checks.values())
    if not chain_consistent:
        raise ValueError("one-cycle artifact chain is inconsistent")

    started=_utc(cycle_started_at,"cycle_started_at")
    completed=_utc(cycle_completed_at,"cycle_completed_at")
    if completed<=started:
        raise ValueError("cycle_completed_at must be after cycle_started_at")
    elapsed_days=(completed-started).total_seconds()/86400
    growth=settlement.get("capital_growth_jpy")
    if isinstance(growth,bool) or not isinstance(growth,(int,float)):
        raise ValueError("settlement capital_growth_jpy required")
    velocity=round(growth/elapsed_days,2)

    mode=_text(proof_mode,"proof_mode",80)
    live_verified=mode=="live_external_verified"

    return {
        "version":PROOF_VERSION,
        "status":"one_cycle_warashibe_proved",
        "proof_key":_text(proof_key,"proof_key",200),
        "proof_mode":mode,
        "item_key":item,
        "quantity":1,
        "chain_consistent":True,
        "chain_checks":chain_checks,
        "starting_capital_jpy":settlement.get("starting_capital_jpy"),
        "capital_basis_jpy":settlement.get("capital_basis_jpy"),
        "actual_net_proceeds_jpy":settlement.get("actual_net_proceeds_jpy"),
        "next_capital_jpy":settlement.get("next_capital_jpy"),
        "capital_growth_jpy":growth,
        "capital_growth_percent":settlement.get("capital_growth_percent"),
        "cycle_started_at":started.isoformat(),
        "cycle_completed_at":completed.isoformat(),
        "cycle_elapsed_days":round(elapsed_days,4),
        "capital_velocity_jpy_per_day":velocity,
        "warashibe_loop_v2_contract_complete":True,
        "live_external_actions_verified":live_verified,
        "ready_for_next_candidate":True,
        "controlled_automation_authorized":False,
        "human_review_required":True,
    }
