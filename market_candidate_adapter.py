# ============================================================
# Warashibe AI v1.1
# Market Candidate Adapter
#
# 役割：
# 仮想市場の商品データを
# Candidate Engine で扱える形式へ変換する。
#
# market_engine.py は変更しない。
# ============================================================

from candidate_engine import create_candidate


ADAPTER_VERSION = "1.3"


# 仮想市場の商品カテゴリー
#
# Demand Engine / Value Engine が
# 商品を評価できるようにする。
CATEGORY_MAP = {
    "わら": "general",
    "古い切手": "collector",
    "小物": "general",
    "雑貨セット": "general",
    "古本セット": "book",
    "限定古書": "book",
    "中古CDセット": "cd",
    "アンティーク小物": "collector",
    "中古ゲーム": "game",
    "コレクターソフト": "game",
    "電子機器": "electronics",
    "工具セット": "tools",
    "ブランド小物": "brand",
    "中古カメラ": "camera",
    "高級中古品": "brand",
    "ヴィンテージ時計": "collector",
    "高額商品": "general",
    "限定家電": "electronics",
    "希少商品": "collector",
}


def get_category(name):
    """商品名からカテゴリーを取得する"""

    return CATEGORY_MAP.get(name, "unknown")


def market_item_to_candidate(item):
    """仮想市場の商品1件をCandidate形式へ変換する"""

    price = item.get("price", 0)
    name = item.get("name", "")
    next_value = item.get("next_value", 0)
    success_rate = item.get("success_rate", 0)

    category = get_category(name)

    return create_candidate(
        name=name,
        purchase_price=price,
        expected_sale_price=next_value,
        source="virtual_market",
        category=category,
        confidence=success_rate,
    )


def market_items_to_candidates(items):
    """仮想市場の商品一覧をCandidate形式へ変換する"""

    return [
        market_item_to_candidate(item)
        for item in items
    ]