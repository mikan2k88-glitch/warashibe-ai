from flask import Blueprint, jsonify, request, render_template_string

from market_engine import MARKET
from policy_engine import POLICY_VERSION, START_CAPITAL
from strategy_engine import STRATEGY_LABELS, create_recommendation

from simulation_engine import (
    TARGET,
    MAX_CAMPAIGN_CYCLES,
    run_cycle,
    summarize_campaigns
)


strategy_bp = Blueprint("strategy", __name__)


def get_strategy():
    strategy = request.args.get(
        "strategy",
        "random"
    ).lower()

    if strategy not in {
        "random",
        "safe",
        "aggressive"
    }:
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
    except ValueError:
        return None

    if minimum <= value <= maximum:
        return value

    return None


def evaluate_strategies(
    campaigns,
    max_cycles
):
    strategy_results = [
        summarize_campaigns(
            strategy,
            campaigns,
            max_cycles
        )
        for strategy in (
            "random",
            "safe",
            "aggressive"
        )
    ]

    recommendation = create_recommendation(
        strategy_results
    )

    ranked_results = sorted(
        strategy_results,
        key=lambda result: (
            -result[
                "campaign_goal_rate_percent"
            ],
            result[
                "average_cycles_used"
            ],
            result[
                "total_restarts"
            ]
        )
    )

    return (
        strategy_results,
        ranked_results,
        recommendation
    )


@strategy_bp.route("/journey")
def journey():

    strategy = get_strategy()

    if strategy is None:
        return jsonify({
            "error": "strategy が不正です。"
        }), 400

    result = run_cycle(strategy)

    return jsonify({
        "version": "1.1",
        "policy_version": POLICY_VERSION,
        "strategy": strategy,
        "start_capital": START_CAPITAL,
        **result
    })


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
        return jsonify({
            "error": "strategy が不正です。"
        }), 400

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

        for trade in result["history"]:

            stats = item_stats[
                trade["selected_item"]
            ]

            stats["attempts"] += 1

            if trade["success"]:
                stats["successes"] += 1
            else:
                stats["failures"] += 1

        if result["status"] == "goal_reached":
            goal_reached += 1

    for stats in item_stats.values():

        attempts = stats["attempts"]

        stats["success_rate_percent"] = (
            round(
                stats["successes"]
                / attempts
                * 100,
                2
            )
            if attempts
            else 0
        )

    return jsonify({
        "version": "1.1",
        "policy_version": POLICY_VERSION,
        "strategy": strategy,
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
        return jsonify({
            "error": "strategy が不正です。"
        }), 400

    if (
        campaigns is None
        or max_cycles is None
    ):
        return jsonify({
            "error":
                "campaigns は1〜10000、"
                "max_cycles は1〜100で指定してください。"
        }), 400

    summary = summarize_campaigns(
        strategy,
        campaigns,
        max_cycles
    )

    return jsonify({
        "version": "1.1",
        "policy_version": POLICY_VERSION,
        "start_capital": START_CAPITAL,
        "target": TARGET,
        **summary
    })


@strategy_bp.route(
    "/strategy/recommendation"
)
def strategy_recommendation():
    """内部連携向けのJSONデータ"""

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

    if (
        campaigns is None
        or max_cycles is None
    ):
        return jsonify({
            "error":
                "campaigns は100〜10000、"
                "max_cycles は1〜100で指定してください。"
        }), 400

    (
        strategy_results,
        _,
        recommendation
    ) = evaluate_strategies(
        campaigns,
        max_cycles
    )

    return jsonify({
        "version": "1.1",
        "policy_version": POLICY_VERSION,
        "mode": "virtual_market_only",
        "current_capital": START_CAPITAL,
        "target": TARGET,
        "strategies": strategy_results,
        "recommendation": recommendation
    })


@strategy_bp.route("/strategy/report")
def strategy_report():
    """人間向けの戦略レポート"""

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

    if (
        campaigns is None
        or max_cycles is None
    ):
        return (
            "campaigns または "
            "max_cycles の指定が不正です。",
            400
        )

    (
        _,
        ranked_results,
        recommendation
    ) = evaluate_strategies(
        campaigns,
        max_cycles
    )

    return render_template_string("""
    <!doctype html>
    <html lang="ja">

    <head>

        <meta charset="utf-8">

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
                    <th>順位</th>
                    <th>戦略</th>
                    <th>100万円到達率</th>
                    <th>平均再挑戦回数</th>
                </tr>

                {% for result
                in ranked_results %}

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
