"""Quality-gated bridge from market estimates to the existing Candidate Pipeline."""

from collections import Counter

from research_lab.evidence_candidate_pipeline import evaluate_market_estimates
from research_lab.market_estimate_quality_gate import evaluate_market_estimate

QUALITY_PIPELINE_VERSION = "0.1"


def evaluate_quality_gated_estimates(estimates, current_capital, **gate_kwargs):
    accepted = []
    rejected = []
    for estimate in estimates:
        gate = evaluate_market_estimate(estimate, **gate_kwargs)
        if gate.accepted:
            accepted.append(estimate)
        else:
            rejected.append({"name": estimate.name, "reasons": list(gate.reasons)})

    result = evaluate_market_estimates(accepted, current_capital)
    result["quality_pipeline_version"] = QUALITY_PIPELINE_VERSION
    result["quality_accepted"] = len(accepted)
    result["quality_rejected"] = len(rejected)
    result["quality_rejections"] = rejected
    result["quality_rejection_reasons"] = dict(
        Counter(reason for row in rejected for reason in row["reasons"])
    )
    return result
