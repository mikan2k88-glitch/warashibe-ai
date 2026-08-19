# Warashibe AI v1.0
# 候補商品の地雷を検出するフィルター

DANGER_FILTER_VERSION = "1.0"

MIN_CONFIDENCE = 0.50
MIN_PROFIT = 0
MIN_PROFIT_RATE = 0.05


def evaluate_candidate(candidate):
    """
    商品候補を評価し、
    危険・情報不足・採算不明な候補を除外する。
    """

    reasons = []

    purchase_price = candidate.get("purchase_price", 0)
    expected_sale_price = candidate.get("expected_sale_price", 0)
    expected_profit = candidate.get("expected_profit", 0)
    expected_profit_rate = candidate.get("expected_profit_rate", 0)
    confidence = candidate.get("confidence", 0)

    if not candidate.get("name"):
        reasons.append("商品名がありません")

    if purchase_price <= 0:
        reasons.append("仕入れ価格が不正です")

    if expected_sale_price <= 0:
        reasons.append("想定売却価格が不正です")

    if expected_sale_price <= purchase_price:
        reasons.append("想定売却価格が仕入れ価格以下です")

    if expected_profit <= MIN_PROFIT:
        reasons.append("期待利益が不足しています")

    if expected_profit_rate < MIN_PROFIT_RATE:
        reasons.append(
            f"期待利益率が最低基準 {MIN_PROFIT_RATE * 100}% 未満です"
        )

    if confidence < MIN_CONFIDENCE:
        reasons.append(
            f"情報信頼度が最低基準 {MIN_CONFIDENCE * 100}% 未満です"
        )

    return {
        "allowed": len(reasons) == 0,
        "filter_version": DANGER_FILTER_VERSION,
        "reasons": reasons,
        "risk_summary": {
            "minimum_confidence": MIN_CONFIDENCE,
            "minimum_profit": MIN_PROFIT,
            "minimum_profit_rate": MIN_PROFIT_RATE
        }
    }


def filter_candidates(candidates):
    """
    複数の商品候補を安全な候補と
    除外された候補に分ける。
    """

    allowed = []
    blocked = []

    for candidate in candidates:
        decision = evaluate_candidate(candidate)

        if decision["allowed"]:
            allowed.append(candidate)
        else:
            blocked.append({
                "candidate": candidate,
                "reasons": decision["reasons"]
            })

    return allowed, blocked
