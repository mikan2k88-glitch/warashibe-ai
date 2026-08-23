# ============================================================
# Candidate Pipeline
#
# 候補商品を
# 1. 危険フィルター
# 2. 資本フィルター
# 3. ランキング
# の順番で処理する。
# ============================================================

from danger_filter import filter_candidates
from capital_filter import filter_by_capital
from ranking_engine import rank_candidates


PIPELINE_VERSION = "1.0"


def evaluate_candidates(
    candidates,
    current_capital
):
    """
    候補商品を一連のフィルターと
    ランキングで評価する。
    """

    # ========================================================
    # 1. 候補商品の安全性チェック
    # ========================================================

    danger_allowed, danger_blocked = (
        filter_candidates(
            candidates
        )
    )

    # ========================================================
    # 2. 現在資本によるフィルター
    # ========================================================

    capital_allowed, capital_blocked = (
        filter_by_capital(
            danger_allowed,
            current_capital
        )
    )

    # ========================================================
    # 3. ランキング
    # ========================================================

    ranked_candidates = rank_candidates(
        capital_allowed
    )

    # ========================================================
    # 4. BEST候補
    # ========================================================

    best_candidate = None

    if ranked_candidates:

        best_candidate = (
            ranked_candidates[0]
        )

    # ========================================================
    # 結果
    # ========================================================

    return {

        "version":
            PIPELINE_VERSION,

        "current_capital":
            current_capital,

        "total_candidates":
            len(candidates),

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
            best_candidate
    }
