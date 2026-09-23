"""Storage and service smoke tests."""

import os
import tempfile

from research_lab.evaluator import Metrics
from research_lab.lab_service import evaluate_and_record
from research_lab.storage import ResearchRepository


def run():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        repository = ResearchRepository(path)
        result = evaluate_and_record(
            track="speed", title="storage smoke test",
            baseline=Metrics(0.40, 20.0, 100.0, True),
            candidate=Metrics(0.40, 15.0, 100.0, True), repository=repository,
        )
        assert result["decision"] == "candidate"
        assert repository.stats()["total"] == 1
        assert repository.recent(1)[0]["candidate"]["conditional_transactions"] == 15.0
    finally:
        if os.path.exists(path): os.remove(path)


if __name__ == "__main__":
    run()
    print("RESEARCH STORAGE: PASSED")
