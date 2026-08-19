# Warashibe AI v1.0
# 市場ごとに異なる商品データを共通フォーマットへ変換する

CANDIDATE_VERSION = "1.0"


def create_candidate(
    name,
    purchase_price,
    expected_sale_price,
    source,
    category="unknown",
    confidence=0.0,
    metadata=None
):
    """
    商品候補をWarashibe AI共通フォーマットへ変換する。

    purchase_price:
        仕入れ価格

    expected_sale_price:
        想定売却価格

    source:
        商品データの取得元

    confidence:
        価格情報などに対する信頼度
        0.0 ～ 1.0
    """

    if metadata is None:
        metadata = {}

    expected_profit = expected_sale_price - purchase_price

    if purchase_price > 0:
        expected_profit_rate = expected_profit / purchase_price
    else:
        expected_profit_rate = 0

    return {
        "candidate_version": CANDIDATE_VERSION,

        "name": name,
        "category": category,
        "source": source,

        "purchase_price": purchase_price,
        "expected_sale_price": expected_sale_price,

        "expected_profit": expected_profit,
        "expected_profit_rate": expected_profit_rate,

        "confidence": confidence,

        "metadata": metadata
    }
