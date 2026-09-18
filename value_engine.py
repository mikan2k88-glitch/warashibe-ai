# Warashibe AI v1.1
# 価値変換エンジン
#
# 役割：
# ・現在の資産価値から次の価値変換可能性を評価する
# ・価値成長率、交換可能性、次の想定価値を返す
#
# 現段階では仮想価値データを使用する。
# 実市場データとの接続は後の段階で行う。


VERSION = "0.2"


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
    "collector": {
        "growth_rate": 1.70,
        "growth_score": 0.75,
        "exchange_potential": 0.78,
        "route": "collector",
    },
    "electronics": {
        "growth_rate": 1.40,
        "growth_score": 0.68,
        "exchange_potential": 0.65,
        "route": "electronics",
    },
    "tools": {
        "growth_rate": 1.50,
        "growth_score": 0.60,
        "exchange_potential": 0.62,
        "route": "specialist",
    },
    "general": {
        "growth_rate": 1.20,
        "growth_score": 0.50,
        "exchange_potential": 0.50,
        "route": "general",
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
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def get_value_transformation(asset):
    if not isinstance(asset, dict):
        asset = {}

    name = asset.get("name", "")
    category = _normalize_category(asset.get("category"))
    current_value = _normalize_value(asset.get("value", 0))

    value = VALUE_DATA.get(category, DEFAULT_VALUE)

    next_value = current_value * value["growth_rate"]

    return {
        "asset": name,
        "category": category,
        "current_value": current_value,
        "next_value": next_value,
        "value_growth_score": value["growth_score"],
        "exchange_potential": value["exchange_potential"],
        "route": value["route"],
    }


def get_value_growth_score(asset):
    value = get_value_transformation(asset)

    return value["value_growth_score"]


def get_next_value(asset):
    value = get_value_transformation(asset)

    return value["next_value"]


def get_exchange_potential(asset):
    value = get_value_transformation(asset)

    return value["exchange_potential"]