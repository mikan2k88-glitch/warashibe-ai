"""PG-051/052 walk-forward validation and champion/challenger contracts."""
from statistics import mean

SAFETY = {
    "human_gate_required": True,
    "external_execution_authorized": False,
    "purchase_authorized": False,
}


def evaluate_walk_forward(windows, *, min_windows=3, min_positive_rate=0.67, max_drawdown_rate=0.35):
    if not isinstance(windows, list):
        windows = []
    reasons = []
    valid = [w for w in windows if isinstance(w, dict)]
    if len(valid) != len(windows):
        reasons.append("invalid_window_record")
    if len(valid) < min_windows:
        reasons.append("insufficient_windows")
    returns = []
    drawdowns = []
    for row in valid:
        r = row.get("return_rate")
        d = row.get("max_drawdown_rate")
        if isinstance(r, bool) or not isinstance(r, (int, float)):
            reasons.append("invalid_return_rate")
            continue
        if isinstance(d, bool) or not isinstance(d, (int, float)) or not 0 <= d <= 1:
            reasons.append("invalid_drawdown_rate")
            continue
        returns.append(r)
        drawdowns.append(d)
    positive_rate = (sum(1 for r in returns if r > 0) / len(returns)) if returns else 0.0
    mean_return = mean(returns) if returns else None
    max_drawdown = max(drawdowns) if drawdowns else None
    if positive_rate < min_positive_rate:
        reasons.append("positive_window_rate_low")
    if max_drawdown is None or max_drawdown > max_drawdown_rate:
        reasons.append("drawdown_too_high")
    reasons = list(dict.fromkeys(reasons))
    passed = not reasons
    return {
        "pg": "PG-051",
        "status": "walk_forward_passed" if passed else "walk_forward_failed",
        "walk_forward_passed": passed,
        "window_count": len(valid),
        "positive_window_rate": positive_rate,
        "mean_return_rate": mean_return,
        "max_drawdown_rate": max_drawdown,
        "reasons": reasons,
        "prospective_evidence_untouched": True,
        **SAFETY,
    }


def evaluate_champion_challenger(*, champion, challenger, walk_forward_result, shadow_result):
    reasons = []
    if not isinstance(champion, dict) or not champion.get("strategy_id"):
        reasons.append("champion_missing")
    if not isinstance(challenger, dict) or not challenger.get("strategy_id"):
        reasons.append("challenger_missing")
    if isinstance(champion, dict) and isinstance(challenger, dict) and champion.get("strategy_id") == challenger.get("strategy_id"):
        reasons.append("same_strategy")
    if walk_forward_result.get("walk_forward_passed") is not True:
        reasons.append("walk_forward_not_passed")
    if shadow_result.get("shadow_passed") is not True:
        reasons.append("shadow_not_passed")
    promotable = not reasons
    return {
        "pg": "PG-052",
        "status": "challenger_review_ready" if promotable else "challenger_blocked",
        "promotion_recommended": promotable,
        "auto_promote": False,
        "active_strategy_unchanged": True,
        "reasons": reasons,
        **SAFETY,
    }
