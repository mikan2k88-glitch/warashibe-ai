"""Seeded, offline aggregate statistics for the one-item virtual journey.

Rates describe the injected fixture and its assumptions, not real-market odds.
"""

from collections import Counter
from math import isfinite
from random import Random

from research_lab.market_decision_virtual_journey import run_virtual_journey

STATISTICS_VERSION = "0.1"


def evaluate_virtual_journeys(provider_factory, query: str, start_capital: float,
                              *, trials: int = 100, seed: int = 0,
                              target: float = 1_000_000, max_steps: int = 20,
                              **gate_kwargs) -> dict:
    """Run independently seeded trials; no global RNG or external mutation."""
    if isinstance(trials, bool) or not isinstance(trials, int) or not 1 <= trials <= 10000:
        raise ValueError("trials must be an integer from 1 to 10000")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or not 1 <= max_steps <= 20:
        raise ValueError("max_steps must be an integer from 1 to 20")
    for key, value in (("start_capital", start_capital), ("target", target)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value <= 0:
            raise ValueError(f"{key} must be finite and positive")
    if not callable(provider_factory):
        raise ValueError("provider_factory must be callable")
    rng = Random(seed)
    counts = Counter()
    final_capital_sum = 0.0
    max_capital_sum = 0.0
    step_sum = 0
    for _ in range(trials):
        draws = tuple(rng.random() for _ in range(max_steps))
        run = run_virtual_journey(provider_factory, query, start_capital, draws,
                                  target=target, max_steps=max_steps, **gate_kwargs)
        counts[run["status"]] += 1
        final_capital_sum += run["final_capital"]
        max_capital_sum += max([start_capital] + [row["capital_after"] for row in run["history"]])
        step_sum += run["steps"]
    return {
        "version": STATISTICS_VERSION, "trials": trials, "seed": seed,
        "start_capital": start_capital, "target": target, "max_steps": max_steps,
        "status_counts": {status: counts[status] for status in
                          ("goal_reached", "failed", "no_candidate", "max_steps_reached")},
        "goal_rate_percent": round(100 * counts["goal_reached"] / trials, 4),
        "average_final_capital": round(final_capital_sum / trials, 2),
        "average_max_capital": round(max_capital_sum / trials, 2),
        "average_steps": round(step_sum / trials, 4),
        "external_action_authorized": False,
    }
