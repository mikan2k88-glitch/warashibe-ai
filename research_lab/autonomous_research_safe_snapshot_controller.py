"""Safe controller for local autonomous-research runner snapshots.

Composes bounded local file loading with freshness-gated decision logic.
It performs no commands, network requests, repository writes, or external
actions.
"""

from research_lab.autonomous_research_fresh_snapshot_decision import (
    decision_from_fresh_snapshot,
)
from research_lab.autonomous_research_snapshot_file_adapter import load_snapshot

SAFE_SNAPSHOT_CONTROLLER_VERSION = "0.1"


def control_from_snapshot_file(
    path,
    *,
    now=None,
    max_age_seconds=None,
    repair_attempts=0,
):
    snapshot = load_snapshot(path)
    decision = decision_from_fresh_snapshot(
        snapshot,
        now=now,
        max_age_seconds=max_age_seconds,
        repair_attempts=repair_attempts,
    )
    return {
        "version": SAFE_SNAPSHOT_CONTROLLER_VERSION,
        "source": "local_snapshot_file",
        "decision": decision["decision"],
        "reason": decision["reason"],
        "stage": decision["stage"],
        "next_theme": decision["next_theme"],
        "fresh": decision["fresh"],
        "notify": decision.get("notify", decision["decision"] == "stop"),
        "external_action_performed": False,
        "credentials_included": False,
    }
