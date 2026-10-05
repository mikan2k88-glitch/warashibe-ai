# ============================================================
# Warashibe AI v1.2
# Candidate Pipeline
#
# 役割：
# 候補商品を
# 1. 危険フィルター
# 2. 資本フィルター
# 3. ランキング
# の順番で処理し、選択結果を共通recordとして返す。
# ============================================================

from danger_filter import filter_candidates
from capital_filter import filter_by_capital
from ranking_engine import rank_candidates


PIPELINE_VERSION = "1.2"


def _build_selection_record(best_candidate, ranked_candidates):
    """PG-006: 後段で保存・監査できる共通の選択recordを作る。"""
    if best_candidate is None:
        reason = "no_candidate_selected"
    else:
        reason = "highest_ranked_allowed_candidate"

    return {
        "selected_candidate": best_candidate,
        "selection_reason": reason,
        "candidate_result": {
            "ranked_count": len(ranked_candidates),
            "selected": best_candidate,
        },
        "strategy_result": {
            "status": "not_applied",
            "strategy": None,
        },
        "simulation_result": None,
    }


def evaluate_candidates(
    candidates,
    current_capital,
    *, shadow_repository=None, shadow_assessment=None, as_of=None,
):
    """
    候補商品を一連のフィルターと
    ランキングで評価する。
    """

    danger_allowed, danger_blocked = (
        filter_candidates(
            candidates
        )
    )

    capital_allowed, capital_blocked = (
        filter_by_capital(
            danger_allowed,
            current_capital
        )
    )

    ranked_candidates = rank_candidates(
        capital_allowed
    )

    best_candidate = None

    if ranked_candidates:
        best_candidate = ranked_candidates[0]

    selection_record = _build_selection_record(
        best_candidate,
        ranked_candidates,
    )

    result = {
        "version": PIPELINE_VERSION,

        "current_capital": current_capital,

        "total_candidates": len(candidates),

        "danger_allowed_count":
            len(danger_allowed),

        "danger_blocked_count":
            len(danger_blocked),

        "capital_allowed_count":
            len(capital_allowed),

        "capital_blocked_count":
            len(capital_blocked),

        "allowed":
            capital_allowed,

        "danger_blocked":
            danger_blocked,

        "capital_blocked":
            capital_blocked,

        "ranked_candidates":
            ranked_candidates,

        "best_candidate":
            best_candidate,

        "selection_record":
            selection_record,
    }
    if shadow_repository is not None:
        from research_lab.shadow_routing import route_selected_to_shadow
        result["shadow_routing"] = route_selected_to_shadow(
            result, repository=shadow_repository, assessment=shadow_assessment, as_of=as_of,
        )
    return result
