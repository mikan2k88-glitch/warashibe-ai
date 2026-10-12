from __future__ import annotations


REQUIRED_TERM_FIELDS = (
    "supplier_dropshipping_permission",
    "platform_terms",
    "return_terms",
    "cancellation_terms",
)


def _explicit_status(candidate: dict, field: str) -> str | None:
    evidence = candidate.get("terms_evidence") or {}
    value = evidence.get(field)
    if isinstance(value, dict):
        value = value.get("status")
    if value is None:
        return None
    return str(value).strip().lower()


def _confirmed(candidate: dict, field: str) -> bool:
    explicit = _explicit_status(candidate, field)
    if explicit is not None:
        return explicit in {"confirmed", "known", "accepted"}

    legacy = {
        "supplier_dropshipping_permission": candidate.get("supplier_allows_dropshipping") is True,
        "platform_terms": candidate.get("platform_terms_confirmed") is True,
        "return_terms": candidate.get("return_terms_confirmed") is True,
        "cancellation_terms": candidate.get("cancellation_terms_confirmed") is True,
    }
    return legacy[field]


def assess_terms_evidence(candidate: dict) -> dict:
    checks = {}
    missing = []
    for field in REQUIRED_TERM_FIELDS:
        confirmed = _confirmed(candidate, field)
        checks[field] = {
            "confirmed": confirmed,
            "status": _explicit_status(candidate, field) or (
                "confirmed_legacy" if confirmed else "unknown"
            ),
        }
        if not confirmed:
            missing.append(field)

    passed = not missing
    return {
        "gate_version": "6.4",
        "status": "terms_complete" if passed else "terms_incomplete",
        "passed": passed,
        "checks": checks,
        "required_fields": list(REQUIRED_TERM_FIELDS),
        "missing_fields": missing,
        "promotion_allowed": passed,
        "live_execution_allowed": False,
    }
