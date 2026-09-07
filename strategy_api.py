from flask import Blueprint, jsonify, request, render_template_string

from market_engine import MARKET
from policy_engine import POLICY_VERSION, START_CAPITAL

from strategy_engine import STRATEGY_LABELS

from simulation_engine import run_cycle

from campaign_engine import (
    TARGET,
    MAX_CAMPAIGN_CYCLES,
    summarize_campaigns,
    evaluate_strategies,
)


VERSION = "1.1"

STRATEGIES = (
    "random",
    "safe",
    "balanced",
    "aggressive",
)


strategy_bp = Blueprint(
    "strategy",
    __name__
)


# ============================================================
# 共通関数
# ============================================================

def get_strategy():
    strategy = request.args.get(
        "strategy",
        "random"
    ).strip().lower()

    if strategy not in STRATEGIES:
        return None

    return strategy


def get_bounded_int(
    name,
    default,
    minimum,
    maximum
):
    value = request.args.get(name)

    if value is None:
        return default

    try:
        value = int(value)
    except (ValueError, TypeError):
        return None

    if minimum <= value <= maximum:
        return value

    return None


def strategy_error():
    return jsonify({
        "error": (
            "strategy が不正です。"
            "使用可能: random, safe, balanced, aggressive"
        )
    }), 400


# ============================================================
# /journey
#
# 1回のわらしべ挑戦
# ============================================================

@strategy_bp.route("/journey")
def journey():

    strategy = get_strategy()

    if strategy is None:
        return strategy_error()

    result = run_cycle(strategy)

    return jsonify({
        "version": VERSION,
        "policy_version": POLICY_VERSION,
        "strategy": strategy,
        "start_capital": START_CAPITAL,
        "target": TARGET,
        **result
    })


# ============================================================
# /simulate
#
# 単体シミュレーション
# ============================================================

@strategy_bp.route("/simulate")
def simulate():

    strategy = get_strategy()

    simulations = get_bounded_int(
        "simulations",
        10_000,
        1,
        100_000
    )

    if strategy is None:
        return strategy_error()

    if simulations is None:
        return jsonify({
            "error":
                "simulations は1〜100000の整数です。"
        }), 400

    goal_reached = 0

    item_stats = {
        item["name"]: {
            "attempts": 0,
            "successes": 0,
            "failures": 0
        }
        for item in MARKET
    }

    for _ in range(simulations):

        result = run_cycle(strategy)

        for trade in result.get(
            "history",
            []
        ):

            item_name = trade.get(
                "selected_item"
            )

            if not item_name:
                continue

            if item_name not in item_stats:
                item_stats[item_name] = {
                    "attempts": 0,
                    "successes": 0,
                    "failures": 0
                }

            stats = item_stats[item_name]

            stats["attempts"] += 1

            if trade.get("success"):
                stats["successes"] += 1
            else:
                stats["failures"] += 1

        if result.get("status") == "goal_reached":
            goal_reached += 1

    for stats in item_stats.values():

        attempts = stats["attempts"]

        if attempts:
            stats["success_rate_percent"] = round(
                stats["successes"]
                / attempts
                * 100,
                2
            )
        else:
            stats["success_rate_percent"] = 0

    return jsonify({
        "version": VERSION,
        "policy_version": POLICY_VERSION,
        "strategy": strategy,
        "start_capital": START_CAPITAL,
        "target": TARGET,
        "simulations": simulations,
        "goal_reached": goal_reached,
        "goal_rate_percent": round(
            goal_reached
            / simulations
            * 100,
            2
        ),
        "item_stats": item_stats
    })


# ============================================================
# /campaign/simulate
#
# 再挑戦ありのキャンペーン統計
#
# 例：
#
# /campaign/simulate
#     ?strategy=balanced
#     &campaigns=1000
#     &max_cycles=10
#
# ============================================================

@strategy_bp.route("/campaign/simulate")
def campaign_simulate():

    strategy = get_strategy()

    campaigns = get_bounded_int(
        "campaigns",
        1_000,
        1,
        10_000
    )

    max_cycles = get_bounded_int(
        "max_cycles",
        MAX_CAMPAIGN_CYCLES,
        1,
        100
    )

    if strategy is None:
        return strategy_error()

    if campaigns is None:
        return jsonify({
            "error":
                "campaigns は1〜10000の整数です。"
        }), 400

    if max_cycles is None:
        return jsonify({
            "error":
                "max_cycles は1〜100の整数です。"
        }), 400

    summary = summarize_campaigns(
        strategy,
        campaigns,
        max_cycles
    )

    return jsonify({
        "version": VERSION,
        "policy_version": POLICY_VERSION,
        "start_capital": START_CAPITAL,
        "target": TARGET,
        **summary
    })


# ============================================================
# /strategy/recommendation
#
# 4戦略を比較
# 内部連携向けJSON
# ============================================================

@strategy_bp.route(
    "/strategy/recommendation"
)
def strategy_recommendation():

    campaigns = get_bounded_int(
        "campaigns",
        1_000,
        100,
        10_000
    )

    max_cycles = get_bounded_int(
        "max_cycles",
        MAX_CAMPAIGN_CYCLES,
        1,
        100
    )

    if campaigns is None:
        return jsonify({
            "error":
                "campaigns は100〜10000の整数です。"
        }), 400

    if max_cycles is None:
        return jsonify({
            "error":
                "max_cycles は1〜100の整数です。"
        }), 400

    (
        strategy_results,
        _,
    ) = evaluate_strategies(
        campaigns,
        max_cycles
    )

    recommendation = None

    if strategy_results:
        from strategy_engine import create_recommendation

        recommendation = create_recommendation(
            strategy_results
        )

    return jsonify({
        "version": VERSION,
        "policy_version": POLICY_VERSION,
        "mode": "virtual_market_only",
        "current_capital": START_CAPITAL,
        "target": TARGET,
        "strategies": strategy_results,
        "recommendation": recommendation
    })


# ============================================================
# /strategy/report
#
# 人間向け戦略レポート
# ============================================================

@strategy_bp.route("/strategy/report")
def strategy_report():

    campaigns = get_bounded_int(
        "campaigns",
        1_000,
        100,
        10_000
    )

    max_cycles = get_bounded_int(
        "max_cycles",
        MAX_CAMPAIGN_CYCLES,
        1,
        100
    )

    if campaigns is None:
        return (
            "campaigns の指定が不正です。",
            400
        )

    if max_cycles is None:
        return (
            "max_cycles の指定が不正です。",
            400
        )

    (
        strategy_results,
        ranked_results,
    ) = evaluate_strategies(
        campaigns,
        max_cycles
    )

    from strategy_engine import create_recommendation

    recommendation = create_recommendation(
        strategy_results
    )

    return render_template_string(
        """
        <!doctype html>

        <html lang="ja">

        <head>

            <meta charset="utf-8">

            <meta
                name="viewport"
                content="width=device-width, initial-scale=1"
            >

            <title>
                Warashibe AI 戦略レポート
            </title>

            <style>

                body {
                    max-width: 760px;
                    margin: 40px auto;
                    padding: 0 20px;
                    font-family: sans-serif;
                    line-height: 1.7;
                    color: #222;
                }

                .card {
                    margin: 18px 0;
                    padding: 20px;
                    border-radius: 12px;
                    background: #f5f7fb;
                }

                .recommendation {
                    background: #e8f5e9;
                    border-left:
                        6px solid #2e7d32;
                }

                .risk {
                    background: #fff3e0;
                    border-left:
                        6px solid #ef6c00;
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                }

                th,
                td {
                    padding: 10px;
                    border-bottom:
                        1px solid #ddd;
                    text-align: left;
                }

            </style>

        </head>

        <body>

            <h1>
                Warashibe AI 戦略レポート
            </h1>

            <p>
                仮想市場で
                {{ campaigns }}
                回のキャンペーンを比較しました。
            </p>


            <div class="card recommendation">

                <h2>
                    今日の結論
                </h2>

                <p>

                    <strong>
                        {{
                            recommendation.
                            recommended_strategy_label
                        }}戦略
                    </strong>

                    を提案します。

                </p>

                <p>
                    {{ recommendation.reason }}
                </p>

                <p>

                    代表的な成功ルート：

                    <br>

                    {{
                        recommendation.
                        dominant_successful_route
                    }}

                </p>

            </div>


            <div class="card">

                <h2>
                    戦略比較
                </h2>

                <table>

                    <tr>

                        <th>
                            順位
                        </th>

                        <th>
                            戦略
                        </th>

                        <th>
                            100万円到達率
                        </th>

                        <th>
                            平均サイクル
                        </th>

                        <th>
                            平均再挑戦
                        </th>

                    </tr>


                    {% for result in ranked_results %}

                    <tr>

                        <td>
                            {{ loop.index }}
                        </td>

                        <td>
                            {{
                                strategy_labels[
                                    result.strategy
                                ]
                            }}
                        </td>

                        <td>
                            {{
                                result.
                                campaign_goal_rate_percent
                            }}%
                        </td>

                        <td>
                            {{
                                result.
                                average_cycles_used
                            }}
                        </td>

                        <td>
                            {{
                                result.
                                average_restarts
                            }}回
                        </td>

                    </tr>

                    {% endfor %}

                </table>

            </div>


            <div class="card risk">

                <h2>
                    注意点
                </h2>

                <p>

                    リスク評価：

                    <strong>
                        {{
                            recommendation.risk_level
                        }}
                    </strong>

                </p>

                <p>

                    これは仮想市場での研究結果です。

                    実際の仕入れ・注文は、
                    必ず人間が確認してから
                    行ってください。

                </p>

            </div>

        </body>

        </html>
        """,

        campaigns=campaigns,

        ranked_results=ranked_results,

        recommendation=recommendation,

        strategy_labels=STRATEGY_LABELS
    )
