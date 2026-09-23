"""Raw sale-outcome calibration for real-market research.

Stores explicit Bernoulli outcomes (sold / not sold) separately from aggregated
market evidence. Beta posterior summaries provide a transparent, updateable
sale-probability estimate without pretending aggregate evidence counts are raw
transaction outcomes. Research only; production Route Engine is unchanged.
"""

from dataclasses import dataclass
from statistics import mean

CALIBRATOR_VERSION = "0.1"


@dataclass(frozen=True)
class SaleOutcome:
    opportunity_key: str
    sold: bool
    days_to_outcome: float | None = None


@dataclass(frozen=True)
class OutcomeCalibration:
    opportunity_key: str
    successes: int
    failures: int
    observations: int
    posterior_alpha: float
    posterior_beta: float
    posterior_mean: float
    empirical_sale_rate: float | None
    mean_days_to_outcome: float | None


def calibrate_outcomes(
    opportunity_key: str,
    outcomes: list[SaleOutcome],
    prior_alpha: float = 1.0,
    prior_beta: float = 1.0,
) -> OutcomeCalibration:
    if prior_alpha <= 0 or prior_beta <= 0:
        raise ValueError("beta prior parameters must be positive")

    matching = [x for x in outcomes if x.opportunity_key == opportunity_key]
    successes = sum(1 for x in matching if x.sold)
    failures = len(matching) - successes

    alpha = prior_alpha + successes
    beta = prior_beta + failures
    posterior_mean = alpha / (alpha + beta)

    days = [float(x.days_to_outcome) for x in matching if x.days_to_outcome is not None]
    empirical = successes / len(matching) if matching else None

    return OutcomeCalibration(
        opportunity_key=opportunity_key,
        successes=successes,
        failures=failures,
        observations=len(matching),
        posterior_alpha=alpha,
        posterior_beta=beta,
        posterior_mean=posterior_mean,
        empirical_sale_rate=empirical,
        mean_days_to_outcome=mean(days) if days else None,
    )
