"""PG-017 approved Human Review -> dry-run commerce plan.

A dry-run plan is an audit artifact only. It never authorizes or triggers
purchase, payment, sale, listing, or any external commerce action.
"""

from datetime import datetime, timezone

PLAN_VERSION = "0.1"


def _require_text(value, name, *, max_length=300):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")
    value = value.strip()
    if len(value) > max_length:
        raise ValueError(f"{name} is too long")
    return value


def _parse_utc(value, name):
    value = _require_text(value, name, max_length=80)
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def build_dry_run_commerce_plan(
    record,
    review,
    *,
    plan_key,
    generated_at,
):
    if not isinstance(record, dict):
        raise ValueError("record must be a dictionary")
    if not isinstance(review, dict):
        raise ValueError("review must be a dictionary")

    record_key = _require_text(record.get("record_key"), "record_key", max_length=200)
    identity_key = _require_text(record.get("identity_key"), "identity_key")
    if review.get("record_key") != record_key:
        raise ValueError("review record_key mismatch")
    if review.get("identity_key") != identity_key:
        raise ValueError("review identity mismatch")
    if str(review.get("decision") or "").lower() != "approve":
        raise ValueError("approved Human Review is required")

    proposal = record.get("proposal") or {}
    if proposal.get("status") != "proposal_ready":
        raise ValueError("proposal_ready record required")
    if proposal.get("human_review_required") is not True:
        raise ValueError("human review contract missing")
    if proposal.get("commerce_authorized") is not False:
        raise ValueError("commerce must remain blocked")
    if review.get("commerce_authorized") is not False:
        raise ValueError("review must not authorize commerce")

    plan_key = _require_text(plan_key, "plan_key", max_length=200)
    generated = _parse_utc(generated_at, "generated_at")
    reviewed = _parse_utc(review.get("reviewed_at"), "reviewed_at")
    if generated < reviewed:
        raise ValueError("generated_at must not be before reviewed_at")

    purchase_price = proposal.get("candidate_purchase_price_jpy")
    if isinstance(purchase_price, bool) or not isinstance(purchase_price, (int, float)):
        raise ValueError("candidate purchase price is required")
    if purchase_price < 0:
        raise ValueError("candidate purchase price must be >= 0")

    return {
        "version": PLAN_VERSION,
        "status": "dry_run_plan_ready",
        "plan_key": plan_key,
        "source_record_key": record_key,
        "identity_key": identity_key,
        "review_decision": "approve",
        "reviewed_at": reviewed.isoformat(),
        "candidate_name": _require_text(proposal.get("candidate_name"), "candidate_name"),
        "candidate_source": _require_text(proposal.get("candidate_source"), "candidate_source"),
        "purchase_price_jpy": int(round(purchase_price)),
        "reference_price_spread_jpy": proposal.get("reference_price_spread_jpy"),
        "generated_at": generated.isoformat(),
        "execution_mode": "dry_run",
        "human_final_confirmation_required": True,
        "execution_triggered": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "purchase_authorized": False,
        "payment_authorized": False,
        "sale_authorized": False,
    }
