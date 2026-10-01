# ============================================================
# Capital Filter
# 現在の資本全額で扱える候補商品を判定
# ============================================================


def evaluate_capital_fit(
    current_capital,
    candidate
):
    """
    現在資本に対して候補商品が適合するか判定する。

    基本ルール：
    - 同一時点では資本全額で1商品だけを扱う
    - 仕入れ価格が現在資本と一致しない候補は除外
    - 仕入れ価格が0以下なら除外

    データ形式：
    - purchase_price を優先
    - 旧market_engine形式の price にも対応
    """

    purchase_price = candidate.get(
        "purchase_price",
        candidate.get("price", 0)
    )

    reasons = []

    if purchase_price <= 0:
        reasons.append(
            "仕入れ価格が0以下です"
        )

    elif purchase_price != current_capital:
        reasons.append(
            f"現在資本 {current_capital} 円を全額使うため、"
            f"仕入れ価格は {current_capital} 円と一致する必要があります"
        )

    allowed = len(reasons) == 0

    return {
        "allowed": allowed,
        "current_capital": current_capital,
        "purchase_price": purchase_price,
        "capital_usage_rate": round(
            purchase_price
            / current_capital,
            4
        )
        if current_capital > 0
        else None,
        "reasons": reasons
    }


def filter_by_capital(
    candidates,
    current_capital
):
    """候補商品を全資本購入ルールでフィルタリングする。"""

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
