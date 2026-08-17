# Warashibe AI v0.8
# AIより上位にある、変更不可のゲームルール

POLICY_VERSION = "0.8"

START_CAPITAL = 100
ONE_ITEM_ONLY = True
FULL_CAPITAL_PURCHASE_REQUIRED = True


def evaluate_trade(capital, item):
    """商品1つの取引がわらしべルールに適合するか判定する"""
    reasons = []

    if not ONE_ITEM_ONLY:
        reasons.append("1商品ルールが無効です")

    if item["price"] > capital:
        reasons.append("現在資本を超える商品は購入できません")

    if FULL_CAPITAL_PURCHASE_REQUIRED and item["price"] != capital:
        reasons.append("現在資本と同額の商品を1つだけ選ぶ必要があります")

    if not 0 < item["success_rate"] <= 1:
        reasons.append("success_rate が不正です")

    if item["next_value"] <= 0:
        reasons.append("next_value が不正です")

    return {
        "allowed": len(reasons) == 0,
        "policy_version": POLICY_VERSION,
        "reasons": reasons,
        "rule_summary": {
            "one_item_only": ONE_ITEM_ONLY,
            "full_capital_purchase_required": FULL_CAPITAL_PURCHASE_REQUIRED
        }
    }
