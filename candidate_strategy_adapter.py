# ============================================================
# Warashibe AI v1.1
# Candidate Strategy Adapter
#
# 役割：
# Candidate形式の候補を
# Strategy Engineで判断できる形式へ変換する。
#
# Candidate PipelineとStrategy Engineを直接結合しない。
# ============================================================

from strategy_engine import select_item


ADAPTER_VERSION = "1.1"


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


def select_candidate(candidates, strategy):
    """Candidate一覧から戦略に応じて1件選択する"""

    if not candidates:
        return None

    strategy_items = candidates_to_strategy_items(candidates)
    selected = select_item(strategy_items, strategy)

    if selected is None:
        return None

    selected_name = selected.get("name")

    for candidate in candidates:
        if candidate.get("name") == selected_name:
            return candidate

    return None
