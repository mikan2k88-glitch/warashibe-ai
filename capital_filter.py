# ============================================================
# Capital Filter
# Candidate形式を共通Policyへ接続する資本フィルター
# ============================================================

from policy_engine import evaluate_trade


def _candidate_to_policy_item(candidate):
    """Candidate形式をpolicy_engineが扱う商品形式へ変換する。"""

    purchase_price = candidate.get(
        "purchase_price",
        candidate.get("price", 0)
    )

    expected_sale_price = candidate.get(
        "expected_sale_price",
        candidate.get("next_value", 0)
    )

    confidence = candidate.get(
        "confidence",
        candidate.get("success_rate", 1.0)
    )

    return {
        "name": candidate.get("name", "candidate"),
        "price": purchase_price,
        "success_rate": confidence,
        "next_value": expected_sale_price if expected_sale_price > 0 else 1,
    }


def evaluate_capital_fit(
    current_capital,
    candidate
):
    """
    Candidateの資本適合を共通Policyで判定する。

    全資本1品ルールの正本はpolicy_engine.evaluate_trade()。
    このモジュールではCandidate形式の変換と表示用情報の付加だけを行う。
    """

    purchase_price = candidate.get(
        "purchase_price",
        candidate.get("price", 0)
    )

    if current_capital <= 0:
        return {
            "allowed": False,
            "current_capital": current_capital,
            "purchase_price": purchase_price,
            "capital_usage_rate": None,
            "policy_version": None,
            "rule_summary": {},
            "reasons": ["現在資本が0以下です"],
        }

    policy_decision = evaluate_trade(
        current_capital,
        _candidate_to_policy_item(candidate)
    )

    return {
        "allowed": policy_decision["allowed"],
        "current_capital": current_capital,
        "purchase_price": purchase_price,
        "capital_usage_rate": round(
            purchase_price / current_capital,
            4
        ),
        "policy_version": policy_decision["policy_version"],
        "rule_summary": policy_decision["rule_summary"],
        "reasons": policy_decision["reasons"],
    }


def filter_by_capital(
    candidates,
    current_capital
):
    """候補商品を共通Policyの資本ルールでフィルタリングする。"""

    allowed = []
    blocked = []

    for candidate in candidates:

        decision = evaluate_capital_fit(
            current_capital,
            candidate
        )

        if decision["allowed"]:

            allowed_candidate = (
                candidate.copy()
            )

            allowed_candidate[
                "capital_fit"
            ] = decision

            allowed.append(
                allowed_candidate
            )

        else:

            blocked.append({
                "candidate": candidate,
                "reasons": decision["reasons"],
                "capital_fit": decision
            })

    return allowed, blocked
