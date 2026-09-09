# Warashibe AI v1.1
# 需要エンジン
#
# 役割：
# ・現在の資産に対する需要を評価する
# ・需要の強さ、鮮度、交換可能性を返す
#
# 現段階では仮想需要データを使用する。
# 実市場APIとの接続は後の段階で行う。


VERSION = "0.1"


# 仮想需要データ
#
# 0.0 ～ 1.0 の範囲で設定する。
DEMAND_DATA = {
    "camera": {
        "demand_score": 0.80,
        "freshness_score": 0.75,
        "exchange_score": 0.70,
        "demand_level": "high",
    },
    "game": {
        "demand_score": 0.75,
        "freshness_score": 0.80,
        "exchange_score": 0.72,
        "demand_level": "high",
    },
    "brand": {
        "demand_score": 0.85,
        "freshness_score": 0.78,
        "exchange_score": 0.80,
        "demand_level": "high",
    },
    "book": {
        "demand_score": 0.40,
        "freshness_score": 0.50,
        "exchange_score": 0.35,
        "demand_level": "low",
    },
    "cd": {
        "demand_score": 0.45,
        "freshness_score": 0.55,
        "exchange_score": 0.40,
        "demand_level": "low",
    },
}


DEFAULT_DEMAND = {
    "demand_score": 0.50,
    "freshness_score": 0.50,
    "exchange_score": 0.50,
    "demand_level": "medium",
}


def _normalize_category(category):
    """カテゴリーを安全に文字列化する。"""

    if category is None:
        return ""

    return str(category).strip().lower()


def get_demand(asset):
    """
    現在の資産に対する需要情報を返す。

    Parameters
    ----------
    asset : dict
        以下の情報を想定する。

        {
            "name": "中古カメラ",
            "value": 5000,
            "category": "camera"
        }

    Returns
    -------
    dict
        需要情報。
    """

    if not isinstance(asset, dict):
        asset = {}

    name = asset.get("name", "")
    category = _normalize_category(asset.get("category"))

    demand = DEMAND_DATA.get(category, DEFAULT_DEMAND)

    return {
        "asset": name,
        "category": category,
        "demand_score": demand["demand_score"],
        "demand_level": demand["demand_level"],
        "freshness_score": demand["freshness_score"],
        "exchange_score": demand["exchange_score"],
    }


def get_demand_level(demand_score):
    """
    需要スコアから需要レベルを判定する。
    """

    try:
        score = float(demand_score)
    except (TypeError, ValueError):
        return "medium"

    if score >= 0.70:
        return "high"

    if score >= 0.40:
        return "medium"

    return "low"


def get_exchange_potential(asset):
    """
    現在の資産が次の価値へ交換される可能性を返す。
    """

    demand = get_demand(asset)

    return demand["exchange_score"]
