# ============================================================
# Capital Filter
# 現在の資本で扱える候補商品を判定
# ============================================================


def evaluate_capital_fit(
    current_capital,
    candidate
):
    """
    現在資本に対して候補商品が適合するか判定する。

    基本ルール：
    - 仕入れ価格が現在資本を超えていたら除外
    - 仕入れ価格が0以下なら除外
    - 資本の範囲内なら購入可能
    """

    purchase_price = candidate.get(
        "purchase_price",
        0
    )

    reasons = []

    # --------------------------------------------------------
    # 資本チェック
    # --------------------------------------------------------

    if purchase_price <= 0:

        reasons.append(
            "仕入れ価格が0以下です"
        )

    elif purchase_price > current_capital:

        reasons.append(
            f"現在資本 {current_capital} 円では "
            f"仕入れ価格 {purchase_price} 円を購入できません"
        )

    # --------------------------------------------------------
    # 判定
    # --------------------------------------------------------

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
    """
    候補商品を現在資本でフィルタリングする。
    """

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
