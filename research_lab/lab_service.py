"""Application service joining evaluation and persistent research memory."""

from dataclasses import asdict

from research_lab.evaluator import Metrics, compare
from research_lab.storage import ResearchRepository


def evaluate_and_record(*, track: str, title: str, baseline: Metrics, candidate: Metrics,
                        notes: str = "", repository: ResearchRepository | None = None):
    repository = repository or ResearchRepository()
    evaluation = compare(baseline, candidate)
    experiment_id = repository.record(
        track=track,
        title=title,
        status="completed",
        baseline=asdict(baseline),
        candidate=asdict(candidate),
        decision=evaluation.status,
        reason=evaluation.reason,
        notes=notes,
    )
    return {"experiment_id": experiment_id, "decision": evaluation.status, "reason": evaluation.reason}
