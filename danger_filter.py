# Warashibe AI v1.1
# Danger Filter
#
# 役割：
# ・候補商品のリスクを評価する
# ・成功率、価値倍率、利益率などからリスク情報を付与する
# ・明らかに不正な候補だけをブロックする
#
# 「危険だから即除外」ではなく、
# Strategy / Ranking が判断できるように
# リスク情報を候補へ付加する。


DANGER_FILTER_VERSION = "1.1"

MIN_CONFIDENCE = 0.10
MIN_PROFIT = 0
MIN_PROFIT_RATE = 0.05


def calculate_multiplier(candidate):
    """仕入れ価格に対する想定売却価格の倍率を計算する"""

    purchase_price = candidate.get("purchase_price", 0)
    expected_sale_price = candidate.get("expected_sale_price", 0)

    if purchase_price <= 0:
        return 0

    return expected_sale_price / purchase_price


def classify_risk(success_rate, multiplier):
    """成功率と価値倍率からリスク区分を決定する"""

    if multiplier >= 8.0:
        if success_rate < 0.40:
            return "high_risk_high_multiplier"
        return "high_multiplier"

    if success_rate >= 0.60:
        return "stable"

    if success_rate >= 0.50:
        return "standard"

    if success_rate >= 0.40:
        return "challenge"

    return "high_risk"


def evaluate_candidate(candidate):
    """候補商品のリスクを評価する"""

    reasons = []

    purchase_price = candidate.get("purchase_price", 0)
    expected_sale_price = candidate.get("expected_sale_price", 0)
    expected_profit = candidate.get("expected_profit", 0)
    expected_profit_rate = candidate.get("expected_profit_rate", 0)
    confidence = candidate.get("confidence", 0)

    multiplier = calculate_multiplier(candidate)

    risk_level = classify_risk(
        confidence,
        multiplier
    )

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

    allowed = len(reasons) == 0

    return {
        "allowed": allowed,
        "filter_version": DANGER_FILTER_VERSION,
        "reasons": reasons,
        "risk_level": risk_level,
        "success_rate": confidence,
        "multiplier": round(multiplier, 2),
        "risk_summary": {
            "minimum_confidence": MIN_CONFIDENCE,
            "minimum_profit": MIN_PROFIT,
            "minimum_profit_rate": MIN_PROFIT_RATE,
        },
    }


def filter_candidates(candidates):
    """候補一覧をリスク評価し、明らかな不正候補だけをブロックする"""

    allowed = []
    blocked = []

    for candidate in candidates:
        decision = evaluate_candidate(candidate)

        if decision["allowed"]:
            allowed_candidate = candidate.copy()

            allowed_candidate["risk"] = {
                "risk_level": decision["risk_level"],
                "success_rate": decision["success_rate"],
                "multiplier": decision["multiplier"],
                "filter_version": decision["filter_version"],
            }

            allowed.append(allowed_candidate)

        else:
            blocked.append(
                {
                    "candidate": candidate,
                    "reasons": decision["reasons"],
                    "risk": {
                        "risk_level": decision["risk_level"],
                        "success_rate": decision["success_rate"],
                        "multiplier": decision["multiplier"],
                        "filter_version": decision["filter_version"],
                    },
                }
            )

    return allowed, blocked