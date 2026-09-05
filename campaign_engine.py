# ============================================================
# Warashibe AI v0.6
# campaign_engine.py
#
# 役割：
# ・1キャンペーン実行
# ・複数キャンペーン集計
# ・複数戦略比較
#
# 1回の挑戦：
# ・simulation_engine.py
#
# 戦略：
# ・strategy_engine.py
#
# 分析：
# ・analysis_engine.py
#
# Web / Flask：
# ・app.py
# ============================================================

from policy_engine import START_CAPITAL

from analysis_engine import (
    create_analysis_stats,
    merge_item_stats,
    merge_capital_band_stats,
)

from simulation_engine import run_cycle


# ============================================================
# 基本設定
# ============================================================

VERSION = "0.6"

TARGET = 1_000_000

MAX_CAMPAIGN_CYCLES = 10


# ============================================================
# 戦略名の正規化
# ============================================================

def normalize_strategy(strategy):
    """
    戦略名を正規化する。

    campaign_engine単体でも利用できるように、
    strategy_engineから取得する。
    """

    from strategy_engine import normalize_strategy as _normalize

    return _normalize(strategy)


# ============================================================
# 失敗ステップ統計合算
# ============================================================

def merge_failure_step_stats(
    total_stats,
    cycle_stats
):
    """
    失敗ステップ統計を合算する。
    """

    for step, stats in cycle_stats.items():

        if step not in total_stats:
            total_stats[step] = {
                "failures": 0,
                "failure_rate_percent": 0.0,
            }

        total_stats[step]["failures"] += int(
            stats.get("failures", 0)
        )

    total_failures = sum(
        stats.get("failures", 0)
        for stats in total_stats.values()
    )

    if total_failures <= 0:
        return

    for stats in total_stats.values():

        stats["failure_rate_percent"] = round(
            stats["failures"]
            / total_failures
            * 100,
            2
        )


# ============================================================
# 1キャンペーン
# ============================================================

def run_campaign(
    strategy,
    max_cycles=MAX_CAMPAIGN_CYCLES
):
    """
    1キャンペーンを実行する。

    1回失敗するとSTART_CAPITALから
    仮想リスタートする。
    """

    strategy = normalize_strategy(strategy)

    if strategy is None:
        return {
            "status": "invalid_strategy",
            "cycles_used": 0,
            "restarts": 0,
            "failure_reasons": {
                "invalid_strategy": 1
            },
            "successful_route": None,
            "detailed_successful_route": None,
            "analysis_stats":
                create_analysis_stats(),
        }

    try:
        max_cycles = int(max_cycles)

    except (TypeError, ValueError):
        max_cycles = MAX_CAMPAIGN_CYCLES

    max_cycles = max(1, max_cycles)

    failure_reasons = {}

    total_analysis_stats = (
        create_analysis_stats()
    )

    # ========================================================
    # 再挑戦
    # ========================================================

    for cycle_number in range(
        1,
        max_cycles + 1
    ):

        cycle_analysis_stats = (
            create_analysis_stats()
        )

        result = run_cycle(
            strategy,
            cycle_analysis_stats
        )

        cycle_stats = result.get(
            "analysis_stats",
            create_analysis_stats()
        )

        # ----------------------------------------------------
        # 商品統計
        # ----------------------------------------------------

        merge_item_stats(
            total_analysis_stats["item_stats"],
            cycle_stats["item_stats"]
        )

        # ----------------------------------------------------
        # 資本帯統計
        # ----------------------------------------------------

        merge_capital_band_stats(
            total_analysis_stats[
                "capital_band_stats"
            ],
            cycle_stats[
                "capital_band_stats"
            ]
        )

        # ----------------------------------------------------
        # 失敗ステップ統計
        # ----------------------------------------------------

        merge_failure_step_stats(
            total_analysis_stats[
                "failure_step_stats"
            ],
            cycle_stats[
                "failure_step_stats"
            ]
        )

        # ----------------------------------------------------
        # ゴール到達
        # ----------------------------------------------------

        if result["status"] == "goal_reached":

            return {
                "status": "goal_reached",
                "cycles_used": cycle_number,
                "restarts": cycle_number - 1,
                "failure_reasons": failure_reasons,
                "successful_route":
                    result.get(
                        "successful_route"
                    ),
                "detailed_successful_route":
                    result.get(
                        "detailed_successful_route"
                    ),
                "analysis_stats":
                    total_analysis_stats,
            }

        # ----------------------------------------------------
        # 失敗理由
        # ----------------------------------------------------

        reason = result.get(
            "failure_reason",
            result.get(
                "status",
                "unknown"
            )
        )

        failure_reasons[reason] = (
            failure_reasons.get(
                reason,
                0
            ) + 1
        )

        # ----------------------------------------------------
        # Policy完全ブロック
        #
        # 同じSTART_CAPITALから再開しても
        # 同じ条件になるため終了。
        # ----------------------------------------------------

        if result["status"] == "policy_blocked":

            return {
                "status": "policy_blocked",
                "cycles_used": cycle_number,
                "restarts": cycle_number - 1,
                "failure_reasons": failure_reasons,
                "successful_route": None,
                "detailed_successful_route": None,
                "analysis_stats":
                    total_analysis_stats,
            }

    # ========================================================
    # 最大キャンペーンサイクル到達
    # ========================================================

    return {
        "status": "max_cycles_reached",
        "cycles_used": max_cycles,
        "restarts": max_cycles - 1,
        "failure_reasons": failure_reasons,
        "successful_route": None,
        "detailed_successful_route": None,
        "analysis_stats":
            total_analysis_stats,
    }


# ============================================================
# 複数キャンペーン集計
# ============================================================

def summarize_campaigns(
    strategy,
    campaigns=1000,
    max_cycles=MAX_CAMPAIGN_CYCLES
):
    """
    複数キャンペーンを実行して統計を作成する。
    """

    strategy = normalize_strategy(strategy)

    if strategy is None:
        return {
            "error": "strategy が不正です。"
        }

    try:
        campaigns = int(campaigns)

    except (TypeError, ValueError):
        campaigns = 1

    campaigns = max(1, campaigns)

    try:
        max_cycles = int(max_cycles)

    except (TypeError, ValueError):
        max_cycles = MAX_CAMPAIGN_CYCLES

    max_cycles = max(1, max_cycles)

    goal_reached = 0

    total_cycles_used = 0

    total_restarts = 0

    failure_reasons = {}

    successful_route_summary = {}

    detailed_route_summary = {}

    total_analysis_stats = (
        create_analysis_stats()
    )

    # ========================================================
    # キャンペーン実行
    # ========================================================

    for _ in range(campaigns):

        result = run_campaign(
            strategy,
            max_cycles
        )

        # ----------------------------------------------------
        # サイクル数
        # ----------------------------------------------------

        total_cycles_used += int(
            result.get(
                "cycles_used",
                0
            )
        )

        # ----------------------------------------------------
        # リスタート数
        # ----------------------------------------------------

        total_restarts += int(
            result.get(
                "restarts",
                0
            )
        )

        # ----------------------------------------------------
        # 失敗理由
        # ----------------------------------------------------

        for (
            reason,
            count
        ) in result.get(
            "failure_reasons",
            {}
        ).items():

            failure_reasons[reason] = (
                failure_reasons.get(
                    reason,
                    0
                ) + int(count)
            )

        # ----------------------------------------------------
        # 分析統計
        # ----------------------------------------------------

        campaign_stats = result.get(
            "analysis_stats",
            create_analysis_stats()
        )

        merge_item_stats(
            total_analysis_stats["item_stats"],
            campaign_stats["item_stats"]
        )

        merge_capital_band_stats(
            total_analysis_stats[
                "capital_band_stats"
            ],
            campaign_stats[
                "capital_band_stats"
            ]
        )

        merge_failure_step_stats(
            total_analysis_stats[
                "failure_step_stats"
            ],
            campaign_stats[
                "failure_step_stats"
            ]
        )

        # ----------------------------------------------------
        # ゴール到達
        # ----------------------------------------------------

        if result.get("status") == "goal_reached":

            goal_reached += 1

            route = result.get(
                "successful_route"
            )

            if route:

                successful_route_summary[
                    route
                ] = (
                    successful_route_summary.get(
                        route,
                        0
                    ) + 1
                )

            detailed_route = result.get(
                "detailed_successful_route"
            )

            if detailed_route:

                detailed_route_summary[
                    detailed_route
                ] = (
                    detailed_route_summary.get(
                        detailed_route,
                        0
                    ) + 1
                )

    # ========================================================
    # 成功ルートを頻度順にする
    # ========================================================

    sorted_routes = dict(
        sorted(
            successful_route_summary.items(),
            key=lambda item: (
                -item[1],
                item[0]
            )
        )
    )

    sorted_detailed_routes = dict(
        sorted(
            detailed_route_summary.items(),
            key=lambda item: (
                -item[1],
                item[0]
            )
        )
    )

    dominant_route = ""

    if sorted_routes:
        dominant_route = next(
            iter(sorted_routes)
        )

    dominant_detailed_route = ""

    if sorted_detailed_routes:
        dominant_detailed_route = next(
            iter(sorted_detailed_routes)
        )

    # ========================================================
    # 平均値
    # ========================================================

    average_cycles_used = round(
        total_cycles_used
        / campaigns,
        2
    )

    average_restarts = round(
        total_restarts
        / campaigns,
        2
    )

    goal_rate = round(
        goal_reached
        / campaigns
        * 100,
        2
    )

    # ========================================================
    # 仮想リスタート寄与
    # ========================================================

    virtual_restart_contribution = (
        total_restarts
        * START_CAPITAL
    )

    # ========================================================
    # 最終結果
    # ========================================================

    return {
        "average_cycles_used":
            average_cycles_used,

        "average_restarts":
            average_restarts,

        "campaign_goal_rate_percent":
            goal_rate,

        "campaign_goal_reached":
            goal_reached,

        "campaigns":
            campaigns,

        "dominant_successful_route":
            dominant_route,

        "dominant_detailed_successful_route":
            dominant_detailed_route,

        "failure_reasons":
            failure_reasons,

        "item_stats":
            total_analysis_stats[
                "item_stats"
            ],

        "failure_step_stats":
            total_analysis_stats[
                "failure_step_stats"
            ],

        "capital_band_stats":
            total_analysis_stats[
                "capital_band_stats"
            ],

        "max_cycles_per_campaign":
            max_cycles,

        "policy_version":
            _get_policy_version(),

        "start_capital":
            START_CAPITAL,

        "strategy":
            strategy,

        "successful_route_summary":
            sorted_routes,

        "detailed_successful_route_summary":
            sorted_detailed_routes,

        "target":
            TARGET,

        "total_restarts":
            total_restarts,

        "version":
            VERSION,

        "virtual_restart_contribution":
            virtual_restart_contribution,
    }


# ============================================================
# 複数戦略比較
# ============================================================

def evaluate_strategies(
    campaigns=1000,
    max_cycles=MAX_CAMPAIGN_CYCLES
):
    """
    4戦略を比較する。
    """

    strategy_results = []

    for strategy in (
        "random",
        "safe",
        "balanced",
        "aggressive"
    ):

        result = summarize_campaigns(
            strategy,
            campaigns,
            max_cycles
        )

        strategy_results.append(result)

    ranked_results = sorted(
        strategy_results,
        key=lambda result: (
            -result.get(
                "campaign_goal_rate_percent",
                0
            ),
            result.get(
                "average_cycles_used",
                999999
            ),
            result.get(
                "total_restarts",
                999999
            )
        )
    )

    return (
        strategy_results,
        ranked_results
    )


# ============================================================
# policy_version取得
# ============================================================

def _get_policy_version():
    """
    policy_engineの実装差に対応する。
    """

    try:
        from policy_engine import POLICY_VERSION

        return POLICY_VERSION

    except ImportError:
        return "unknown"
