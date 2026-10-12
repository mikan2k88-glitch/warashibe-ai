from __future__ import annotations


REQUIRED_COST_FIELDS = (
    "supplier_cost",
    "supplier_shipping",
    "platform_fee_rate",
    "payment_fee_rate",
    "expected_return_cost",
    "refund_reserve",
)

KNOWN_STATUSES = {"known", "confirmed", "not_applicable"}


def _explicit_status(candidate: dict, field: str) -> str | None:
    evidence = candidate.get("cost_evidence") or {}
    value = evidence.get(field)
    if isinstance(value, dict):
        value = value.get("status")
    if value is None:
        return None
    return str(value).strip().lower()


def _field_present(candidate: dict, field: str) -> bool:
    return field in candidate and candidate.get(field) is not None


def assess_cost_completeness(candidate: dict) -> dict:
    checks = {}
    unknown_fields = []
    legacy_assumptions = []

    for field in REQUIRED_COST_FIELDS:
        explicit = _explicit_status(candidate, field)
        if explicit is not None:
            known = explicit in KNOWN_STATUSES
            status = explicit
        elif _field_present(candidate, field):
            known = True
            status = "known_legacy"
            legacy_assumptions.append(field)
        else:
            known = False
            status = "unknown"

        checks[field] = {
            "known": known,
            "status": status,
            "value": candidate.get(field),
        }
        if not known:
            unknown_fields.append(field)

    passed = not unknown_fields
    return {
        "gate_version": "6.4",
        "status": "cost_complete" if passed else "cost_incomplete",
        "passed": passed,
        "checks": checks,
        "required_fields": list(REQUIRED_COST_FIELDS),
        "unknown_fields": unknown_fields,
        "legacy_assumptions": legacy_assumptions,
        "economics_reliable_for_promotion": passed,
        "promotion_allowed": passed,
        "live_execution_allowed": False,
    }
