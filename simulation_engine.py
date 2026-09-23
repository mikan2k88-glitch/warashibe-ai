# ============================================================
# Warashibe AI v1.0
# simulation_engine.py
#
# 役割：
# ・1回のわらしべ挑戦
# ・Candidate方式の実験
# ・Route Ranking方式の実験
#
# キャンペーン：
# ・campaign_engine.py
#
# 戦略：
# ・strategy_engine.py
#
# Route：
# ・route_engine.py
#
# Candidate評価：
# ・market_candidate_adapter.py
# ・candidate_pipeline.py
# ・candidate_strategy_adapter.py
#
# 分析：
# ・analysis_engine.py
#
# Web / Flask：
# ・app.py
# ============================================================

import random

from market_engine import find_items
from policy_engine import START_CAPITAL, evaluate_trade

from market_engine import MARKET
from market_candidate_adapter import market_items_to_candidates
from candidate_pipeline import evaluate_candidates
from candidate_strategy_adapter import select_candidate

from route_engine import select_route_candidate

from analysis_engine import (
    create_analysis_stats,
    update_analysis_stats,
    finalize_analysis_stats,
    build_successful_route,
    build_detailed_successful_route,
)

from strategy_engine import (
    normalize_strategy,
    get_success_rate,
    get_next_value,
    calculate_balanced_score,
    select_item,
    get_adaptive_strategy,
)


# ============================================================
# 基本設定
# ============================================================

VERSION = "1.0"

TARGET = 1_000_000

MAX_STEPS = 20


# ============================================================
# Candidate評価
# ============================================================

def evaluate_market_candidates(capital):
    """
    仮想市場の商品をCandidate形式へ変換し、
    Candidate Pipelineで評価する。

    既存のsimulation_engineの商品選択ロジックは
    通常戦略について維持する。

    Route戦略では、この関数をcandidate_providerとして
    route_engine.pyへ渡す。
    """

    candidates = market_items_to_candidates(
        MARKET
    )

    return evaluate_candidates(
        candidates,
        current_capital=capital
    )


# ============================================================
# Candidate + Strategyによる商品選択
# ============================================================

def select_candidate_item(capital, strategy):
    """
    Candidate Pipelineで評価された候補から、
    現在資本に近い価格帯を優先したうえで
    Strategyに応じて1商品を選択する。

    route戦略の場合は、
    route_engine.pyを使用して
    最終TARGET到達確率が最大となる候補を選択する。

    既存のrun_cycle()とは分離する。
    """

    strategy = normalize_strategy(
        strategy
    )

    if strategy is None:
        return None

    # ========================================================
    # Route戦略
    # ========================================================

    if strategy == "route":
        return select_route_candidate(
            capital=capital,
            target=TARGET,
            candidate_provider=evaluate_market_candidates,
        )

    # ========================================================
    # 既存戦略
    # ========================================================

    effective_strategy = get_adaptive_strategy(
        capital
    ) if strategy == "adaptive" else strategy

    result = evaluate_market_candidates(
        capital
    )

    candidates = result.get(
        "allowed",
        []
    )

    if not candidates:
        return None

    return select_candidate(
        candidates,
        effective_strategy,
        capital
    )


# ============================================================
# Candidate方式：1回のわらしべ挑戦
# ============================================================

def run_candidate_cycle(
    strategy,
    analysis_stats=None
):
    """
    Candidate方式で1回のわらしべ挑戦を実行する。

    既存のrun_cycle()とは独立して動作する。

    現在資本以下で購入可能なCandidateを
    Candidate Pipelineで評価し、
    現在資本に最も近い価格帯へ絞り込み、
    Strategyにより次の商品を選択する。

    route戦略では、
    最終TARGET到達確率が最大となる
    Route Ranking候補を選択する。

    失敗：
        status = failed

    目標到達：
        status = goal_reached

    候補なし：
        status = no_candidate
    """

    strategy = normalize_strategy(
        strategy
    )

    if strategy is None:
        return {
            "status": "invalid_strategy",
            "final_capital": START_CAPITAL,
            "steps": 0,
            "history": [],
            "failure_reason": "invalid_strategy",
        }

    capital = START_CAPITAL
    history = []

    if analysis_stats is None:
        analysis_stats = create_analysis_stats()

    # ========================================================
    # 最大ステップまで実行
    # ========================================================

    for step in range(
        1,
        MAX_STEPS + 1
    ):

        # ----------------------------------------------------
        # Candidate選択
        # ----------------------------------------------------

        effective_strategy = (
            get_adaptive_strategy(capital)
            if strategy == "adaptive"
            else strategy
        )

        candidate = select_candidate_item(
            capital,
            strategy
        )

        if candidate is None:
            return {
                "status": "no_candidate",
                "final_capital": capital,
                "steps": step - 1,
                "history": history,
                "failure_reason": "no_candidate",
                "analysis_stats": finalize_analysis_stats(
                    analysis_stats
                ),
            }

        # ----------------------------------------------------
        # 商品情報
        # ----------------------------------------------------

        item_name = candidate.get(
            "name",
            "unknown"
        )

        price = candidate.get(
            "purchase_price",
            0
        )

        next_value = candidate.get(
            "expected_sale_price",
            0
        )

        success_rate = candidate.get(
            "confidence",
            0
        )

        # ----------------------------------------------------
        # 成功判定
        # ----------------------------------------------------

        random_value = random.random()

        success = (
            random_value < success_rate
        )

        # ----------------------------------------------------
        # 取引記録
        # ----------------------------------------------------

        trade = {
            "step": step,
            "capital_before": capital,
            "selected_item": item_name,
            "price": price,
            "next_value": next_value,
            "success_rate": success_rate,
            "success_rate_percent": round(
                success_rate * 100,
                2
            ),
            "random_value": random_value,
            "success": success,
            "strategy": strategy,
            "effective_strategy": effective_strategy,
            "source": candidate.get(
                "source",
                ""
            ),
            "candidate_score": candidate.get(
                "score",
                0
            ),
        }

        # ----------------------------------------------------
        # Balancedスコア
        # ----------------------------------------------------

        if strategy == "balanced":

            trade["balanced_score"] = (
                candidate.get(
                    "score",
                    0
                )
            )

        # ----------------------------------------------------
        # Route情報
        # ----------------------------------------------------

        if strategy == "route":

            trade["route_goal_probability"] = (
                candidate.get(
                    "route_goal_probability",
                    0
                )
            )

            trade["route_goal_probability_percent"] = round(
                candidate.get(
                    "route_goal_probability",
                    0
                ) * 100,
                6
            )

            trade["route_future_probability"] = (
                candidate.get(
                    "route_future_probability",
                    0
                )
            )

            trade["route_engine_version"] = (
                candidate.get(
                    "route_engine_version",
                    ""
                )
            )

        # ----------------------------------------------------
        # 成功
        # ----------------------------------------------------

        if success:

            capital = next_value

            trade["capital_after"] = (
                capital
            )

            history.append(trade)

            # ------------------------------------------------
            # ゴール到達
            # ------------------------------------------------

            if capital >= TARGET:

                update_analysis_stats(
                    analysis_stats,
                    history,
                    True
                )

                return {
                    "status": "goal_reached",
                    "final_capital": capital,
                    "steps": step,
                    "history": history,
                    "successful_route":
                        build_successful_route(
                            history
                        ),
                    "detailed_successful_route":
                        build_detailed_successful_route(
                            history
                        ),
                    "analysis_stats":
                        finalize_analysis_stats(
                            analysis_stats
                        ),
                }

        # ----------------------------------------------------
        # 失敗
        # ----------------------------------------------------

        else:

            trade["capital_after"] = 0

            trade["failure_reason"] = (
                "trade_failed"
            )

            history.append(trade)

            update_analysis_stats(
                analysis_stats,
                history,
                False
            )

            return {
                "status": "failed",
                "final_capital": 0,
                "steps": step,
                "history": history,
                "failure_reason": "trade_failed",
                "analysis_stats":
                    finalize_analysis_stats(
                        analysis_stats
                    ),
            }

    # ========================================================
    # 最大ステップ到達
    # ========================================================

    update_analysis_stats(
        analysis_stats,
        history,
        False
    )

    return {
        "status": "max_steps_reached",
        "final_capital": capital,
        "steps": MAX_STEPS,
        "history": history,
        "failure_reason": "max_steps_reached",
        "analysis_stats":
            finalize_analysis_stats(
                analysis_stats
            ),
    }


# ============================================================
# Policyによる選択可能商品取得
# ============================================================

def get_policy_allowed_items(capital):
    """
    現在資本で購入可能な商品を取得し、
    policyで許可された商品だけを返す。
    """

    allowed_items = []
    blocked_items = []

    items = find_items(capital)

    if items is None:
        items = []

    for item in items:

        decision = evaluate_trade(
            capital,
            item
        )

        if decision.get(
            "allowed",
            False
        ):
            allowed_items.append(item)

        else:
            blocked_items.append({
                "item": item.get(
                    "name",
                    "unknown"
                ),
                "reasons": decision.get(
                    "reasons",
                    []
                ),
            })

    return (
        allowed_items,
        blocked_items
    )


# ============================================================
# 成功判定
# ============================================================

def determine_success(item):
    """
    商品のsuccess_rateに基づいて成功判定する。
    """

    success_rate = get_success_rate(
        item
    )

    random_value = random.random()

    success = (
        random_value < success_rate
    )

    return (
        success,
        random_value
    )


# ============================================================
# 既存方式：1回のわらしべ挑戦
# ============================================================

def run_cycle(
    strategy,
    analysis_stats=None
):
    """
    START_CAPITALから開始して、
    1回分のわらしべ挑戦を実行する。

    既存のシミュレーションルールを維持する。

    注意：
    route戦略はCandidate Pipelineを必要とするため、
    run_candidate_cycle()側で使用する。
    """

    strategy = normalize_strategy(
        strategy
    )

    if strategy is None:
        return {
            "status": "invalid_strategy",
            "final_capital": START_CAPITAL,
            "steps": 0,
            "history": [],
            "failure_reason": "invalid_strategy",
        }

    # ========================================================
    # RouteはCandidate方式専用
    # ========================================================

    if strategy == "route":
        return run_candidate_cycle(
            strategy,
            analysis_stats
        )

    capital = START_CAPITAL
    history = []

    if analysis_stats is None:
        analysis_stats = create_analysis_stats()

    for step in range(
        1,
        MAX_STEPS + 1
    ):

        (
            available_items,
            blocked_items
        ) = get_policy_allowed_items(
            capital
        )

        if not available_items:
            return {
                "status": "policy_blocked",
                "final_capital": capital,
                "steps": step - 1,
                "history": history,
                "blocked_items": blocked_items,
                "failure_reason":
                    "policy_blocked",
                "analysis_stats":
                    analysis_stats,
            }

        effective_strategy = (
            get_adaptive_strategy(capital)
            if strategy == "adaptive"
            else strategy
        )

        item = select_item(
            available_items,
            effective_strategy
        )

        if item is None:
            return {
                "status": "no_item",
                "final_capital": capital,
                "steps": step - 1,
                "history": history,
                "failure_reason": "no_item",
                "analysis_stats":
                    analysis_stats,
            }

        item_name = item.get(
            "name",
            "unknown"
        )

        price = item.get(
            "price",
            0
        )

        next_value = get_next_value(
            item
        )

        success_rate = get_success_rate(
            item
        )

        (
            success,
            random_value
        ) = determine_success(item)

        policy = evaluate_trade(
            capital,
            item
        )

        trade = {
            "step": step,
            "capital_before": capital,
            "selected_item": item_name,
            "price": price,
            "next_value": next_value,
            "success_rate": success_rate,
            "success_rate_percent": round(
                success_rate * 100,
                2
            ),
            "random_value": random_value,
            "success": success,
            "strategy": strategy,
            "effective_strategy": effective_strategy,
            "policy": policy,
        }

        if strategy == "balanced":

            trade["balanced_score"] = (
                calculate_balanced_score(
                    item
                )
            )

        if success:

            capital = next_value

            trade["capital_after"] = (
                capital
            )

            history.append(trade)

            if capital >= TARGET:

                update_analysis_stats(
                    analysis_stats,
                    history,
                    True
                )

                return {
                    "status":
                        "goal_reached",
                    "final_capital":
                        capital,
                    "steps": step,
                    "history":
                        history,
                    "successful_route":
                        build_successful_route(
                            history
                        ),
                    "detailed_successful_route":
                        build_detailed_successful_route(
                            history
                        ),
                    "analysis_stats":
                        finalize_analysis_stats(
                            analysis_stats
                        ),
                }

        else:

            trade["capital_after"] = 0

            trade["failure_reason"] = (
                "trade_failed"
            )

            history.append(trade)

            update_analysis_stats(
                analysis_stats,
                history,
                False
            )

            return {
                "status": "failed",
                "final_capital": 0,
                "steps": step,
                "history": history,
                "failure_reason":
                    "trade_failed",
                "analysis_stats":
                    finalize_analysis_stats(
                        analysis_stats
                    ),
            }

    update_analysis_stats(
        analysis_stats,
        history,
        False
    )

    return {
        "status":
            "max_steps_reached",
        "final_capital": capital,
        "steps": MAX_STEPS,
        "history": history,
        "failure_reason":
            "max_steps_reached",
        "analysis_stats":
            analysis_stats,
    }