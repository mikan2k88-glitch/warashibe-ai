"""Read a runner snapshot file and bridge it to a safe research decision.

Only local JSON metadata is accepted. The adapter performs no commands,
network requests, repository writes, or external actions.
"""

import json
from pathlib import Path

from research_lab.autonomous_research_runner_snapshot_bridge import decision_from_snapshot

SNAPSHOT_FILE_ADAPTER_VERSION = "0.1"
MAX_SNAPSHOT_BYTES = 1_000_000


def load_snapshot(path):
    snapshot_path = Path(path)
    if not snapshot_path.is_file():
        raise ValueError("snapshot file is required")
    if snapshot_path.stat().st_size > MAX_SNAPSHOT_BYTES:
        raise ValueError("snapshot file is too large")

    try:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid snapshot file") from exc

    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must contain a JSON object")
    return snapshot


def decision_from_snapshot_file(path, *, repair_attempts=0):
    snapshot = load_snapshot(path)
    decision = decision_from_snapshot(snapshot, repair_attempts=repair_attempts)
    return {
        "version": SNAPSHOT_FILE_ADAPTER_VERSION,
        "source": "local_snapshot_file",
        "stage": decision["stage"],
        "next_theme": decision["next_theme"],
        "decision": decision["decision"],
        "reason": decision["reason"],
        "notify": decision["notify"],
        "external_action_performed": False,
        "credentials_included": False,
    }
