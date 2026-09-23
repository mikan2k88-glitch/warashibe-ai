"""Tests for the research-only sale outcome store."""

import tempfile
from pathlib import Path

from research_lab.live_outcome_store import OutcomeStore
from research_lab.raw_outcome_calibration import SaleOutcome


def run():
    with tempfile.TemporaryDirectory() as tmp:
        store = OutcomeStore(Path(tmp) / "outcomes.json")
        assert store.stats()["mode"] == "waiting"
        store.append(SaleOutcome("camera-a", True, 4.0))
        store.append(SaleOutcome("camera-a", False, 8.0))
        store.append(SaleOutcome("book-b", True, 2.0))
        rows = store.for_opportunity("camera-a")
        assert len(rows) == 2
        assert rows[0].sold is True
        assert rows[1].sold is False
        stats = store.stats()
        assert stats == {"mode": "persisted_research", "total": 3, "sold": 2, "failed": 1, "opportunities": 2}


if __name__ == "__main__":
    run()
    print("LIVE OUTCOME STORE: PASSED")
