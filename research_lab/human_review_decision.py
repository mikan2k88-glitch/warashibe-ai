"""Human review decision contract for PG-016.

Review decisions are append-only audit records. Approval means only that a human
reviewed and accepted the proposal for further consideration. It never authorizes
purchase, payment, sale, or any external action.
"""

from datetime import datetime, timezone

from research_lab.cross_market_record import evaluate_cross_market_record_freshness

REVIEW_VERSION = "0.1"
ALLOWED_DECISIONS = {"approve", "reject"}


def _require_text(value, name, *, max_length=500):
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


def evaluate_review_eligibility(record, *, now=None, max_age_seconds=3600):
    freshness = evaluate_cross_market_record_freshness(
        record,
        now=now,
        max_age_seconds=max_age_seconds,
    )
    ready = (
        freshness.get("status") == "fresh"
        and (record.get("proposal") or {}).get("status") == "proposal_ready"
        and (record.get("proposal") or {}).get("human_review_required") is True
        and (record.get("proposal") or {}).get("commerce_authorized") is False
    )
    return {
        "status": "review_ready" if ready else "review_blocked",
        "review_allowed": ready,
        "freshness": freshness,
        "commerce_authorized": False,
        "external_action_authorized": False,
    }


def build_human_review_decision(
    record,
    *,
    decision,
    reviewer_id,
    reason,
    reviewed_at,
    now=None,
    max_age_seconds=3600,
):
    if not isinstance(record, dict):
        raise ValueError("record must be a dictionary")

    eligibility = evaluate_review_eligibility(
        record,
        now=now,
        max_age_seconds=max_age_seconds,
    )
    if eligibility["review_allowed"] is not True:
        raise ValueError("record is not fresh or reviewable")

    decision = _require_text(decision, "decision", max_length=16).lower()
    if decision not in ALLOWED_DECISIONS:
        raise ValueError("decision must be approve or reject")

    reviewer_id = _require_text(reviewer_id, "reviewer_id", max_length=100)
    reason = _require_text(reason, "reason", max_length=1000)
    reviewed = _parse_utc(reviewed_at, "reviewed_at")

    if now is not None:
        now_utc = now.astimezone(timezone.utc)
        if reviewed > now_utc:
            raise ValueError("reviewed_at must not be in the future")

    record_key = _require_text(record.get("record_key"), "record_key", max_length=200)
    identity_key = _require_text(record.get("identity_key"), "identity_key", max_length=300)

    return {
        "version": REVIEW_VERSION,
        "record_key": record_key,
        "identity_key": identity_key,
        "decision": decision,
        "reviewer_id": reviewer_id,
        "reason": reason,
        "reviewed_at": reviewed.isoformat(),
        "human_review_completed": True,
        "proposal_status": (record.get("proposal") or {}).get("status"),
        "commerce_authorized": False,
        "external_action_authorized": False,
        "purchase_authorized": False,
        "payment_authorized": False,
        "sale_authorized": False,
    }
