"""Implementation review for live scheduled-supervisor connectors.

Selects the implementation order and review status for scheduler, Gemini, and
Codex live connectors. This module performs no live connection, secret access,
external API call, or runtime activation.
"""

LIVE_RUNTIME_CONNECTOR_IMPLEMENTATION_REVIEW_VERSION = "0.1"

IMPLEMENTATION_ORDER = (
    "scheduler",
    "gemini",
    "codex",
)

CONNECTOR_IMPLEMENTATION_STATUS = (
    "design_ready",
    "implementation_ready",
    "blocked",
    "implemented_unverified",
    "verified",
)


def build_connector_implementation_review(
    scheduler_ready=True,
    gemini_ready=True,
    codex_ready=False,
):
    reviews = {
        "scheduler": {
            "design_ready": bool(scheduler_ready),
            "implementation_status": (
                "implementation_ready" if scheduler_ready else "blocked"
            ),
            "requires_secret_read": False,
            "requires_live_external_call": False,
            "recommended_first": True,
        },
        "gemini": {
            "design_ready": bool(gemini_ready),
            "implementation_status": (
                "implementation_ready" if gemini_ready else "blocked"
            ),
            "requires_secret_read": False,
            "requires_live_external_call": True,
            "recommended_first": False,
        },
        "codex": {
            "design_ready": bool(codex_ready),
            "implementation_status": (
                "implementation_ready" if codex_ready else "blocked"
            ),
            "requires_secret_read": False,
            "requires_live_external_call": True,
            "recommended_first": False,
        },
    }

    next_connector = None
    for connector in IMPLEMENTATION_ORDER:
        if reviews[connector]["implementation_status"] == "implementation_ready":
            next_connector = connector
            break

    blockers = []
    if not scheduler_ready:
        blockers.append("scheduler_design_not_ready")
    if not gemini_ready:
        blockers.append("gemini_design_not_ready")
    if not codex_ready:
        blockers.append("codex_callable_runtime_not_available")

    return {
        "version": LIVE_RUNTIME_CONNECTOR_IMPLEMENTATION_REVIEW_VERSION,
        "mode": "review_only",
        "implementation_order": IMPLEMENTATION_ORDER,
        "reviews": reviews,
        "next_connector": next_connector,
        "blockers": tuple(blockers),
        "scheduler_can_be_implemented_first": scheduler_ready is True,
        "gemini_live_call_requires_separate_activation_gate": True,
        "codex_live_call_requires_callable_runtime": True,
        "live_implementation_authorized": False,
        "secret_access_authorized": False,
        "external_action_authorized": False,
    }


def validate_live_runtime_connector_implementation_review(report):
    if not isinstance(report, dict):
        return {
            "valid": False,
            "errors": ("report_not_mapping",),
        }

    errors = []

    if tuple(report.get("implementation_order") or ()) != IMPLEMENTATION_ORDER:
        errors.append("invalid_implementation_order")

    reviews = report.get("reviews")
    if not isinstance(reviews, dict):
        errors.append("invalid_reviews")
    else:
        for connector in IMPLEMENTATION_ORDER:
            if connector not in reviews:
                errors.append(f"missing_{connector}_review")

    if report.get("gemini_live_call_requires_separate_activation_gate") is not True:
        errors.append("gemini_activation_gate_requirement_missing")

    if report.get("codex_live_call_requires_callable_runtime") is not True:
        errors.append("codex_callable_runtime_requirement_missing")

    if report.get("live_implementation_authorized") is not False:
        errors.append("unexpected_live_implementation_authorization")

    if report.get("secret_access_authorized") is not False:
        errors.append("unexpected_secret_access_authorization")

    if report.get("external_action_authorized") is not False:
        errors.append("unexpected_external_action_authorization")

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
        "next_connector": report.get("next_connector"),
        "external_action_authorized": False,
    }


def build_live_runtime_connector_implementation_review_design():
    return {
        "version": LIVE_RUNTIME_CONNECTOR_IMPLEMENTATION_REVIEW_VERSION,
        "mode": "design_only",
        "implementation_order": IMPLEMENTATION_ORDER,
        "scheduler_first": True,
        "gemini_after_scheduler": True,
        "codex_after_callable_runtime_exists": True,
        "no_secret_read_during_review": True,
        "no_live_external_call_during_review": True,
        "live_implementation_authorized": False,
        "external_action_authorized": False,
    }


def validate_live_runtime_connector_implementation_review_design():
    design = build_live_runtime_connector_implementation_review_design()
    assert design["mode"] == "design_only"
    assert design["implementation_order"] == ("scheduler", "gemini", "codex")
    assert design["scheduler_first"] is True
    assert design["gemini_after_scheduler"] is True
    assert design["codex_after_callable_runtime_exists"] is True
    assert design["no_secret_read_during_review"] is True
    assert design["no_live_external_call_during_review"] is True
    assert design["live_implementation_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
