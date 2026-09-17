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


ADAPTER_VERSION = "1.2"


# 仮想市場の商品カテゴリー
#
# Demand Engine / Value Engine が
# 商品を評価できるようにする。
CATEGORY_MAP = {
    "中古カメラ": "camera",
    "中古ゲーム": "game",
    "ブランド小物": "brand",
    "古本セット": "book",
    "中古CDセット": "cd",
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
    """仮想市場の商品一覧をCandidate一覧へ変換する"""

    return [
        market_item_to_candidate(item)
        for item in items
    ]