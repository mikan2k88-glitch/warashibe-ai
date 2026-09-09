# ============================================================
# Warashibe AI v1.1
# value_engine.py
#
# 役割：
# ・現在の資産価値を評価する
# ・次に狙える価値を推定する
# ・価値上昇の可能性を評価する
# ・次の交換可能性を評価する
# ・価値変換ルートを返す
#
# 現段階では仮想データを使用する。
# 実市場データとの接続は後の段階で行う。
# ============================================================

VERSION = "0.1"


VALUE_DATA = {
    "camera": {
        "growth_rate": 1.50,
        "growth_score": 0.72,
        "exchange_potential": 0.68,
        "route": "collector",
    },
    "game": {
        "growth_rate": 1.45,
        "growth_score": 0.70,
        "exchange_potential": 0.72,
        "route": "collector",
    },
    "brand": {
        "growth_rate": 1.60,
        "growth_score": 0.78,
        "exchange_potential": 0.80,
        "route": "brand",
    },
    "book": {
        "growth_rate": 1.20,
        "growth_score": 0.40,
        "exchange_potential": 0.35,
        "route": "used_market",
    },
    "cd": {
        "growth_rate": 1.15,
        "growth_score": 0.35,
        "exchange_potential": 0.30,
        "route": "used_market",
    },
}


DEFAULT_VALUE = {
    "growth_rate": 1.20,
    "growth_score": 0.50,
    "exchange_potential": 0.50,
    "route": "general",
}


def _normalize_category(category):
    if category is None:
        return ""

    return str(category).strip().lower()


def _normalize_value(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0

    if value < 0:
        return 0

    return value


def get_value_transformation(asset):
    """
    現在の資産から次の価値への変換可能性を評価する。
    """

    if not isinstance(asset, dict):
        asset = {}

    name = asset.get("name", "")
    category = _normalize_category(
        asset.get("category")
    )
    current_value = _normalize_value(
        asset.get("value")
    )

    data = VALUE_DATA.get(
        category,
        DEFAULT_VALUE,
    )

    next_value = current_value * data["growth_rate"]

    return {
        "asset": name,
        "category": category,
        "current_value": current_value,
        "next_value": next_value,
        "value_growth_score": data["growth_score"],
        "exchange_potential": data["exchange_potential"],
        "route": data["route"],
    }


def get_value_growth_score(asset):
    """
    価値上昇の可能性だけを返す。
    """

    result = get_value_transformation(asset)

    return result["value_growth_score"]


def get_next_value(asset):
    """
    次に狙える推定価値を返す。
    """

    result = get_value_transformation(asset)

    return result["next_value"]


def get_exchange_potential(asset):
    """
    次の資産へ交換できる可能性を返す。
    """

    result = get_value_transformation(asset)

    return result["exchange_potential"]