"""Offline campaign: restart a new journey at 3,000 JPY after full loss.

Restart is a NEW attempt, never an intra-trade capital injection. Partial-loss salvage stays within the same attempt; it is not a restart.
"""

from research_lab.market_decision_virtual_journey import run_virtual_journey

CAMPAIGN_VERSION = "0.1"
RESTART_CAPITAL_JPY = 3000


def run_virtual_campaign(provider_factory, query: str, attempt_draws: tuple,
                         *, restart_capital: float = RESTART_CAPITAL_JPY,
                         target: float = 1_000_000, max_steps: int = 20,
                         salvage_on_failure: bool = False,
                         **gate_kwargs) -> dict:
    """Consume explicit draw sequences; restart only after a zero-capital failure."""
    if not isinstance(attempt_draws, tuple) or not 1 <= len(attempt_draws) <= 100:
        raise ValueError("attempt_draws must contain 1 to 100 attempts")
    if isinstance(restart_capital, bool) or restart_capital != RESTART_CAPITAL_JPY:
        raise ValueError("restart_capital must be the agreed 3000 JPY baseline")
    attempts = []
    for index, draws in enumerate(attempt_draws, 1):
        result = run_virtual_journey(provider_factory, query, restart_capital,
                                     draws, target=target, max_steps=max_steps,
                                     salvage_on_failure=salvage_on_failure,
                                     **gate_kwargs)
        attempts.append({"attempt": index, **result})
        if result["status"] != "failed" or result["final_capital"] != 0:
            break
    last = attempts[-1]
    return {"version": CAMPAIGN_VERSION, "status": last["status"],
            "attempts": attempts, "attempt_count": len(attempts),
            "restart_count": len(attempts) - 1, "restart_capital": restart_capital,
            "final_capital": last["final_capital"],
            "external_action_authorized": False}
