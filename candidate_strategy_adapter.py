# ============================================================
# Warashibe AI v1.2
# Candidate Strategy Adapter
#
# 役割：
# Candidate形式の候補を
# Strategy Engineで判断できる形式へ変換する。
#
# Candidate PipelineとStrategy Engineを直接結合しない。
#
# 価格選択：
# 現在資本に最も近い購入価格の商品を優先する。
# ============================================================

from strategy_engine import select_item


ADAPTER_VERSION = "1.2"


def candidate_to_strategy_item(candidate):
    """CandidateをStrategy Engine用の形式へ変換する"""

    return {
        "name": candidate.get("name", ""),
        "price": candidate.get("purchase_price", 0),
        "success_rate": candidate.get("confidence", 0),
        "next_value": candidate.get("expected_sale_price", 0),
        "candidate_score": candidate.get("score", 0),
    }


def candidates_to_strategy_items(candidates):
    """Candidate一覧をStrategy Engine用の形式へ変換する"""

    return [
        candidate_to_strategy_item(candidate)
        for candidate in candidates
    ]


def filter_by_price_band(candidates, capital):
    """
    現在資本に最も近い購入価格の商品だけを残す。

    現在資本以下の商品を対象とし、
    その中で最も高い購入価格を優先する。
    """

    if not candidates:
        return []

    affordable = [
        candidate
        for candidate in candidates
        if candidate.get("purchase_price", 0) <= capital
    ]

    if not affordable:
        return []

    max_price = max(
        candidate.get("purchase_price", 0)
        for candidate in affordable
    )

    return [
        candidate
        for candidate in affordable
        if candidate.get("purchase_price", 0) == max_price
    ]


def select_candidate(candidates, strategy, capital=None):
    """
    Candidate一覧から戦略に応じて1件選択する。

    capitalが指定された場合：
        現在資本に最も近い価格帯へ絞り込んでから
        Strategyで選択する。

    capitalが指定されない場合：
        従来どおり全候補からStrategyで選択する。
    """

    if not candidates:
        return None

    if capital is not None:
        candidates = filter_by_price_band(
            candidates,
            capital
        )

    if not candidates:
        return None

    strategy_items = candidates_to_strategy_items(
        candidates
    )

    selected = select_item(
        strategy_items,
        strategy
    )

    if selected is None:
        return None

    selected_name = selected.get(
        "name"
    )

    for candidate in candidates:

        if candidate.get("name") == selected_name:
            return candidate

    return None