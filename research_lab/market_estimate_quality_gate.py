"""Quality gate for market estimates before decision/ranking research."""

from dataclasses import dataclass

from research_lab.market_evidence_estimator import MarketEstimate

QUALITY_GATE_VERSION = "0.1"


@dataclass(frozen=True)
class QualityGateResult:
    accepted: bool
    reasons: tuple[str, ...]


def evaluate_market_estimate(
    estimate: MarketEstimate,
    *,
    min_confidence: float = 0.50,
    min_evidence_count: int = 3,
    min_source_count: int = 2,
) -> QualityGateResult:
    """Fail closed when an estimate lacks independent, credible evidence."""
    reasons = []
    if estimate.confidence < min_confidence:
        reasons.append("low_confidence")
    if estimate.evidence_count < min_evidence_count:
        reasons.append("insufficient_evidence")
    if estimate.source_count < min_source_count:
        reasons.append("insufficient_source_diversity")
    if estimate.purchase_price < 0 or estimate.expected_sale_price < 0:
        reasons.append("invalid_price")
    if not 0.0 <= estimate.sale_probability <= 1.0:
        reasons.append("invalid_sale_probability")
    return QualityGateResult(accepted=not reasons, reasons=tuple(reasons))
