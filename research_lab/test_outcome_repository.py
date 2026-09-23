"""Contract tests for outcome repository abstraction."""

import tempfile
from pathlib import Path

from research_lab.live_outcome_store import OutcomeStore
from research_lab.outcome_repository import validate_repository
from research_lab.raw_outcome_calibration import SaleOutcome


def main():
    with tempfile.TemporaryDirectory() as directory:
        repository = validate_repository(OutcomeStore(Path(directory) / "outcomes.json"))
        assert repository.load() == []
        assert repository.append(SaleOutcome("camera-a", True, 2.0)) == 1
        assert repository.append(SaleOutcome("camera-a", False, 5.0)) == 2
        assert len(repository.for_opportunity("camera-a")) == 2
        assert repository.stats()["total"] == 2

    try:
        validate_repository(object())
    except TypeError:
        pass
    else:
        raise AssertionError("invalid repository must be rejected")

    print("outcome repository abstraction: PASS")


if __name__ == "__main__":
    main()
