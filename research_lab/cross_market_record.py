"""Cross-market record and freshness contract for PG-015."""

from datetime import datetime, timezone

RECORD_VERSION = "0.1"


def _parse_utc(value, field_name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"{field_name} must include timezone")
    return dt.astimezone(timezone.utc)


def build_cross_market_record(
    *,
    record_key,
    comparison,
    proposal,
    observed_at,
    captured_at,
):
    if not isinstance(record_key, str) or not record_key.strip():
        raise ValueError("record_key must be a non-empty string")
    if len(record_key.strip()) > 200:
        raise ValueError("record_key is too long")
    if not isinstance(comparison, dict) or comparison.get("status") != "comparison_ready":
        raise ValueError("comparison_ready record required")
    if comparison.get("same_identity") is not True:
        raise ValueError("same identity is required")
    if not isinstance(proposal, dict) or proposal.get("status") != "proposal_ready":
        raise ValueError("proposal_ready record required")
    if proposal.get("human_review_required") is not True:
        raise ValueError("human review must be required")
    if proposal.get("commerce_authorized") is not False:
        raise ValueError("commerce must remain blocked")

    observed = _parse_utc(observed_at, "observed_at")
    captured = _parse_utc(captured_at, "captured_at")
    if captured < observed:
        raise ValueError("captured_at must not be before observed_at")

    identity_type = comparison.get("identity_type")
    identity_value = comparison.get("identity_value")
    currency = comparison.get("currency")
    if not identity_type or not identity_value or not currency:
        raise ValueError("comparison identity is incomplete")

    return {
        "version": RECORD_VERSION,
        "record_key": record_key.strip(),
        "identity_key": f"{identity_type}:{identity_value}:{str(currency).upper()}",
        "comparison": dict(comparison),
        "proposal": dict(proposal),
        "observed_at": observed.isoformat(),
        "captured_at": captured.isoformat(),
        "commerce_authorized": False,
        "external_action_authorized": False,
    }


def evaluate_cross_market_record_freshness(
    record,
    *,
    now=None,
    max_age_seconds=3600,
):
    if not isinstance(record, dict):
        raise ValueError("record must be a dictionary")
    if max_age_seconds < 0:
        raise ValueError("max_age_seconds must be >= 0")

    observed = _parse_utc(record.get("observed_at"), "observed_at")
    captured = _parse_utc(record.get("captured_at"), "captured_at")
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)

    if captured < observed:
        return {
            "status": "invalid_timestamp_order",
            "review_allowed": False,
            "age_seconds": None,
            "commerce_authorized": False,
        }

    age = (now - observed).total_seconds()
    if age < 0:
        return {
            "status": "future",
            "review_allowed": False,
            "age_seconds": age,
            "commerce_authorized": False,
        }
    if age > max_age_seconds:
        return {
            "status": "stale",
            "review_allowed": False,
            "age_seconds": age,
            "commerce_authorized": False,
        }

    return {
        "status": "fresh",
        "review_allowed": True,
        "age_seconds": age,
        "commerce_authorized": False,
    }
