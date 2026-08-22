# ============================================================
# Warashibe AI v1.2
# 資本適合フィルター
#
# わらしべルール：
# ・現在の資本と同額の商品だけ選択可能
# ・購入可能な候補と除外候補を分離する
# ============================================================


def filter_by_capital(
    candidates,
    current_capital
):
    """
    現在の資本に適合する候補商品を分離する。

    Warashibe Policy:
    FULL_CAPITAL_PURCHASE_REQUIRED = True

    そのため、
    purchase_price == current_capital
    の候補だけを通過させる。
    """

    allowed = []
    blocked = []

    for candidate in candidates:

        purchase_price = candidate.get(
            "purchase_price"
        )

        if purchase_price == current_capital:

            allowed.append(
                candidate
            )

        else:

            blocked.append({

                "candidate": candidate,

                "reasons": [

                    (
                        "現在資本 "
                        f"{current_capital}円 "
                        "と仕入れ価格 "
                        f"{purchase_price}円 "
                        "が一致しません"
                    )

                ]

            })

    return allowed, blocked


def get_capital_summary(
    candidates,
    current_capital
):
    """
    資本フィルターの結果を
    API用の共通フォーマットで返す。
    """

    allowed, blocked = filter_by_capital(
        candidates,
        current_capital
    )

    return {

        "current_capital":
            current_capital,

        "total_candidates":
            len(candidates),

        "capital_matched_count":
            len(allowed),

        "capital_blocked_count":
            len(blocked),

        "capital_matched":
            allowed,

        "capital_blocked":
            blocked
    }
