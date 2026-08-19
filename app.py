from flask import Flask, jsonify, request, render_template_string
import random

from market_engine import MARKET, find_items
from policy_engine import POLICY_VERSION, START_CAPITAL, evaluate_trade
from strategy_engine import STRATEGY_LABELS, create_recommendation

# Warashibe AI v1.0
# 候補商品共通フォーマット
from candidate_engine import create_candidate

# Warashibe AI v1.0
# AI地雷フィルター
from danger_filter import filter_candidates


app = Flask(__name__)

TARGET = 1_000_000
MAX_STEPS = 20
MAX_CAMPAIGN_CYCLES = 10


@app.route("/")
def home():
    return "Warashibe AI v1.0"


@app.route("/docs")
def docs():
    return """
    <h1>Warashibe AI v1.0 API</h1>

    <ul>
        <li>
            <a href="/strategy/report">
                戦略レポート
            </a>
            ：人間向けの結論表示
        </li>

        <li>
            <a href="/journey?strategy=random">
                /journey
            </a>
            ：1回の取引
        </li>

        <li>
            <a href="/simulate?strategy=random">
                /simulate
            </a>
            ：1サイクルの統計
        </li>

        <li>
            <a href="/campaign/simulate?strategy=random">
                /campaign/simulate
            </a>
            ：再挑戦ありの統計
        </li>

        <li>
            <a href="/strategy/recommendation">
                /strategy/recommendation
            </a>
            ：内部用JSON
        </li>

        <li>
            <a href="/candidates/test">
                /candidates/test
            </a>
            ：候補商品＋地雷フィルターのテスト
        </li>
    </ul>
    """


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


def select_item(items, strategy):

    if strategy == "safe":
        return max(
            items,
            key=lambda item: item["success_rate"]
        )

    if strategy == "aggressive":
        return max(
            items,
            key=lambda item: item["next_value"]
        )

    return random.choice(items)


def get_policy_allowed_items(capital):

    allowed_items = []
    blocked_items = []

    for item in find_items(capital):

        decision = evaluate_trade(
            capital,
            item
        )

        if decision["allowed"]:

            allowed_items.append(
                item
            )

        else:

            blocked_items.append({
                "item": item["name"],
                "reasons": decision["reasons"]
            })

    return allowed_items, blocked_items


def run_cycle(strategy):
    """
    100円から開始する、
    1回分のわらしべサイクル
    """

    capital = START_CAPITAL
    history = []

    for step in range(
        1,
        MAX_STEPS + 1
    ):

        available_items, blocked_items = (
            get_policy_allowed_items(
                capital
            )
        )

        if not available_items:

            return {
                "status": "policy_blocked",
                "final_capital": capital,
                "steps": step - 1,
                "history": history,
                "blocked_items": blocked_items
            }

        item = select_item(
            available_items,
            strategy
        )

        success = (
            random.random()
            < item["success_rate"]
        )

        trade = {
            "step": step,
            "capital_before": capital,
            "selected_item": item["name"],
            "price": item["price"],
            "next_value": item["next_value"],
            "success_rate": item["success_rate"],
            "success": success,
            "policy": evaluate_trade(
                capital,
                item
            )
        }

        if success:

            capital = item["next_value"]

            trade["capital_after"] = capital

            history.append(
                trade
            )

            if capital >= TARGET:

                return {
                    "status": "goal_reached",
                    "final_capital": capital,
                    "steps": step,
                    "history": history
                }

        else:

            trade["capital_after"] = 0

            trade["failure_reason"] = (
                "trade_failed"
            )

            history.append(
                trade
            )

            return {
                "status": "failed",
                "final_capital": 0,
                "steps": step,
                "history": history,
                "failure_reason": (
                    "trade_failed"
                )
            }

    return {
        "status": "max_steps_reached",
        "final_capital": capital,
        "steps": MAX_STEPS,
        "history": history
    }


def run_campaign(
    strategy,
    max_cycles
):
    """
    失敗したら100円から再開する、
    複数サイクルの挑戦
    """

    failure_reasons = {}

    for cycle_number in range(
        1,
        max_cycles + 1
    ):

        result = run_cycle(
            strategy
        )

        if (
            result["status"]
            == "goal_reached"
        ):

            route = " → ".join(
                trade["selected_item"]
                for trade in result["history"]
            )

            return {
                "status": "goal_reached",
                "cycles_used": cycle_number,
                "restarts": cycle_number - 1,
                "failure_reasons": failure_reasons,
                "successful_route": route
            }

        reason = result.get(
            "failure_reason",
            result["status"]
        )

        failure_reasons[reason] = (
            failure_reasons.get(
                reason,
                0
            ) + 1
        )

        # 同じルールで再開しても
        # 解決できないため終了
        if (
            result["status"]
            == "policy_blocked"
        ):

            return {
                "status": "policy_blocked",
                "cycles_used": cycle_number,
                "restarts": cycle_number - 1,
                "failure_reasons": failure_reasons
            }

    return {
        "status": "max_cycles_reached",
        "cycles_used": max_cycles,
        "restarts": max_cycles - 1,
        "failure_reasons": failure_reasons
    }


def summarize_campaigns(
    strategy,
    campaigns,
    max_cycles
):
    """
    指定戦略のキャンペーン結果を集計する
    """

    goal_reached = 0

    total_cycles_used = 0

    total_restarts = 0

    failure_reasons = {}

    successful_route_summary = {}

    for _ in range(campaigns):

        result = run_campaign(
            strategy,
            max_cycles
        )

        total_cycles_used += (
            result["cycles_used"]
        )

        total_restarts += (
            result["restarts"]
        )

        for reason, count in (
            result["failure_reasons"]
            .items()
        ):

            failure_reasons[reason] = (
                failure_reasons.get(
                    reason,
                    0
                ) + count
            )

        if (
            result["status"]
            == "goal_reached"
        ):

            goal_reached += 1

            route = (
                result["successful_route"]
            )

            successful_route_summary[
                route
            ] = (
                successful_route_summary.get(
                    route,
                    0
                ) + 1
            )

    sorted_routes = dict(
        sorted(
            successful_route_summary.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )

    dominant_route = next(
        iter(sorted_routes),
        None
    )

    return {
        "strategy": strategy,
        "campaigns": campaigns,
        "max_cycles_per_campaign": max_cycles,

        "campaign_goal_reached": (
            goal_reached
        ),

        "campaign_goal_rate_percent": round(
            goal_reached
            / campaigns
            * 100,
            2
        ),

        "average_cycles_used": round(
            total_cycles_used
            / campaigns,
            2
        ),

        "total_restarts": total_restarts,

        "average_restarts": round(
            total_restarts
            / campaigns,
            2
        ),

        "virtual_restart_contribution": (
            total_restarts
            * START_CAPITAL
        ),

        "failure_reasons": failure_reasons,

        "dominant_successful_route": (
            dominant_route
        ),

        "successful_route_summary": (
            sorted_routes
        )
    }


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

    recommendation = (
        create_recommendation(
            strategy_results
        )
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


# ==========================================
# v0.9
# 1回のわらしべ挑戦
# ==========================================

@app.route("/journey")
def journey():

    strategy = get_strategy()

    if strategy is None:

        return jsonify({
            "error":
            "strategy が不正です。"
        }), 400

    result = run_cycle(
        strategy
    )

    return jsonify({

        "version": "1.0",

        "policy_version":
        POLICY_VERSION,

        "strategy":
        strategy,

        "start_capital":
        START_CAPITAL,

        **result
    })


# ==========================================
# v0.9
# 単体シミュレーション
# ==========================================

@app.route("/simulate")
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
            "error":
            "strategy が不正です。"
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

        result = run_cycle(
            strategy
        )

        for trade in (
            result["history"]
        ):

            stats = item_stats[
                trade["selected_item"]
            ]

            stats["attempts"] += 1

            if trade["success"]:

                stats["successes"] += 1

            else:

                stats["failures"] += 1

        if (
            result["status"]
            == "goal_reached"
        ):

            goal_reached += 1

    for stats in (
        item_stats.values()
    ):

        attempts = stats[
            "attempts"
        ]

        stats[
            "success_rate_percent"
        ] = (

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

        "version": "1.0",

        "policy_version":
        POLICY_VERSION,

        "strategy":
        strategy,

        "simulations":
        simulations,

        "goal_reached":
        goal_reached,

        "goal_rate_percent":
        round(
            goal_reached
            / simulations
            * 100,
            2
        ),

        "item_stats":
        item_stats
    })


# ==========================================
# v0.9
# 再挑戦ありキャンペーン
# ==========================================

@app.route("/campaign/simulate")
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
            "error":
            "strategy が不正です。"
        }), 400

    if (
        campaigns is None
        or max_cycles is None
    ):

        return jsonify({
            "error":
            "campaigns は1〜10000、"
            "max_cyclesは1〜100で指定してください。"
        }), 400

    summary = summarize_campaigns(
        strategy,
        campaigns,
        max_cycles
    )

    return jsonify({

        "version": "1.0",

        "policy_version":
        POLICY_VERSION,

        "start_capital":
        START_CAPITAL,

        "target":
        TARGET,

        **summary
    })


# ==========================================
# v0.9
# AI戦略本部 内部JSON
# ==========================================

@app.route("/strategy/recommendation")
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

    if (
        campaigns is None
        or max_cycles is None
    ):

        return jsonify({
            "error":
            "campaigns は100〜10000、"
            "max_cyclesは1〜100で指定してください。"
        }), 400

    strategy_results, _, recommendation = (
        evaluate_strategies(
            campaigns,
            max_cycles
        )
    )

    return jsonify({

        "version": "1.0",

        "policy_version":
        POLICY_VERSION,

        "mode":
        "virtual_market_only",

        "current_capital":
        START_CAPITAL,

        "target":
        TARGET,

        "strategies":
        strategy_results,

        "recommendation":
        recommendation
    })


# ==========================================
# v0.9
# 人間向け戦略レポート
# ==========================================

@app.route("/strategy/report")
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

    if (
        campaigns is None
        or max_cycles is None
    ):

        return (
            "campaigns または "
            "max_cycles の指定が不正です。",
            400
        )

    _, ranked_results, recommendation = (
        evaluate_strategies(
            campaigns,
            max_cycles
        )
    )

    return render_template_string(
        """
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
                    border-left: 6px solid #2e7d32;
                }

                .risk {
                    background: #fff3e0;
                    border-left: 6px solid #ef6c00;
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                }

                th,
                td {
                    padding: 10px;
                    border-bottom: 1px solid #ddd;
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
                        recommendation.recommended_strategy_label
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
                    recommendation.dominant_successful_route
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
                            平均再挑戦回数
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
                            result.campaign_goal_rate_percent
                            }}%

                        </td>

                        <td>

                            {{
                            result.average_restarts
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


# ==========================================
# v1.0
# 候補商品＋AI地雷フィルター テスト
# ==========================================

@app.route("/candidates/test")
def candidates_test():

    candidates = [

        create_candidate(
            name="安全な中古カメラ",

            purchase_price=10000,

            expected_sale_price=15000,

            source="test",

            category="camera",

            confidence=0.90
        ),

        create_candidate(
            name="利益が低すぎる商品",

            purchase_price=10000,

            expected_sale_price=10200,

            source="test",

            category="misc",

            confidence=0.90
        ),

        create_candidate(
            name="情報不足の商品",

            purchase_price=10000,

            expected_sale_price=20000,

            source="test",

            category="misc",

            confidence=0.30
        ),

        create_candidate(
            name="赤字商品",

            purchase_price=10000,

            expected_sale_price=8000,

            source="test",

            category="misc",

            confidence=0.90
        )
    ]

    allowed, blocked = filter_candidates(
        candidates
    )

    return jsonify({

        "version": "1.0",

        "total_candidates":
        len(candidates),

        "allowed_count":
        len(allowed),

        "blocked_count":
        len(blocked),

        "allowed":
        allowed,

        "blocked":
        blocked
    })


if __name__ == "__main__":
    app.run(debug=True)
