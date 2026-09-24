"""Checks aggregate closed-loop observability without exposing raw outcomes."""

import tempfile
from pathlib import Path

from research_lab.closed_loop_observability import closed_loop_observability
from research_lab.live_outcome_store import OutcomeStore
from research_lab.raw_outcome_calibration import SaleOutcome


class Snapshot:
    provider_count = 2
    raw_count = 5
    observations = (1, 2, 3, 4)


class Freshness:
    accepted = (1, 2, 3)
    stale = 1
    missing_timestamp = 0


def main():
    with tempfile.TemporaryDirectory() as tmp:
        store = OutcomeStore(Path(tmp) / "outcomes.json")
        store.append(SaleOutcome("jpy:camera:a", True, 4))
        metrics = closed_loop_observability(
            snapshot=Snapshot(), freshness=Freshness(),
            estimates=[1, 2], accepted_estimates=[1], rejected_estimates=[2],
            store=store,
        )
        assert metrics["market"]["providers"] == 2
        assert metrics["market"]["fresh_evidence"] == 3
        assert metrics["quality"] == {"estimates": 2, "accepted": 1, "rejected": 1}
        assert metrics["learning"]["total"] == 1
        assert "rows" not in metrics["learning"]
    print("closed-loop observability tests passed")


if __name__ == "__main__":
    main()
