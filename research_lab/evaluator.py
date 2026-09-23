"""Evaluation rules for research results."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Metrics:
    goal_probability: float
    conditional_transactions: float | None = None
    expected_loss: float | None = None
    tests_passed: bool = False


@dataclass(frozen=True)
class Evaluation:
    status: str
    reason: str


def compare(baseline: Metrics, candidate: Metrics) -> Evaluation:
    if not candidate.tests_passed:
        return Evaluation("reject", "candidate tests failed")

    if candidate.goal_probability + 1e-12 < baseline.goal_probability:
        return Evaluation("hold", "goal probability decreased")

    speed_better = (
        baseline.conditional_transactions is not None
        and candidate.conditional_transactions is not None
        and candidate.conditional_transactions < baseline.conditional_transactions
    )
    loss_better = (
        baseline.expected_loss is not None
        and candidate.expected_loss is not None
        and candidate.expected_loss < baseline.expected_loss
    )
    goal_better = candidate.goal_probability > baseline.goal_probability + 1e-12

    if goal_better or speed_better or loss_better:
        return Evaluation("candidate", "at least one objective improved without reducing goal probability")

    return Evaluation("hold", "no material improvement detected")
