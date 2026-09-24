"""Gate runner decisions on snapshot freshness.

Only fresh snapshots may reach the runner decision bridge. Stale or
future-dated snapshots stop safely without performing external actions.
"""

from research_lab.autonomous_research_runner_snapshot_bridge import decision_from_snapshot
from research_lab.autonomous_research_snapshot_freshness_gate import snapshot_freshness

FRESH_SNAPSHOT_DECISION_VERSION = "0.1"


def decision_from_fresh_snapshot(
    snapshot,
    *,
    now=None,
    max_age_seconds=None,
    repair_attempts=0,
):
    freshness_kwargs = {"now": now}
    if max_age_seconds is not None:
        freshness_kwargs["max_age_seconds"] = max_age_seconds
    freshness = snapshot_freshness(snapshot, **freshness_kwargs)

    if not freshness["fresh"]:
        return {
            "version": FRESH_SNAPSHOT_DECISION_VERSION,
            "decision": "stop",
            "reason": freshness["reason"],
            "stage": snapshot.get("stage") if isinstance(snapshot, dict) else None,
            "next_theme": snapshot.get("next_theme") if isinstance(snapshot, dict) else None,
            "fresh": False,
            "external_action_performed": False,
        }

    decision = decision_from_snapshot(snapshot, repair_attempts=repair_attempts)
    return {
        "version": FRESH_SNAPSHOT_DECISION_VERSION,
        "decision": decision["decision"],
        "reason": decision["reason"],
        "stage": decision["stage"],
        "next_theme": decision["next_theme"],
        "fresh": True,
        "notify": decision["notify"],
        "external_action_performed": False,
    }
