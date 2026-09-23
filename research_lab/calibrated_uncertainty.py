"""Calibrated evidence-count uncertainty for observed market routes.

Research-only empirical-Bernstein-style probability radius. The interval uses
effective evidence count and observed sale probability; source diversity and
evidence quality conservatively reduce effective sample size. It is not yet a
formal confidence interval because current MarketEstimate stores aggregated
evidence counts rather than raw Bernoulli sale outcomes.
"""

from math import log, sqrt

from research_lab.real_market_route_bridge import MarketRouteTransition

CALIBRATION_VERSION = "0.1"


def effective_sample_size(transition: MarketRouteTransition) -> float:
    evidence = max(1.0, float(transition.evidence_count))
    source_factor = min(1.0, max(1.0, float(transition.source_count)) / 3.0)
    quality = max(0.05, min(1.0, float(transition.evidence_confidence)))
    return max(1.0, evidence * source_factor * quality)


def calibrated_probability_radius(
    transition: MarketRouteTransition,
    delta: float = 0.10,
) -> float:
    if not 0.0 < delta < 1.0:
        raise ValueError("delta must be between 0 and 1")

    p = max(0.0, min(1.0, float(transition.success_probability)))
    n = effective_sample_size(transition)
    log_term = log(3.0 / delta)
    variance = p * (1.0 - p)

    radius = sqrt(2.0 * variance * log_term / n) + 3.0 * log_term / n
    return min(1.0, radius)


def calibrated_probability_band(
    transition: MarketRouteTransition,
    delta: float = 0.10,
) -> tuple[float, float]:
    p = max(0.0, min(1.0, float(transition.success_probability)))
    radius = calibrated_probability_radius(transition, delta)
    return max(0.0, p - radius), min(1.0, p + radius)
