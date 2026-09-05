from flask import Flask, jsonify, request, render_template_string

from market_engine import MARKET
from policy_engine import POLICY_VERSION, START_CAPITAL

from strategy_engine import (
    STRATEGY_LABELS,
    create_recommendation
)

from simulation_engine import run_cycle
from campaign_engine import summarize_campaigns, evaluate_strategies



# ============================================================
# Warashibe AI v1.1
#
# Flask API / Web UI
#
# シミュレーション本体
#     → simulation_engine.py
#
# 候補商品API
#     → candidate_api.py
#
# 候補商品パイプライン
#     → candidate_pipeline.py
#
# ============================================================


app = Flask(__name__)

from candidate_api import candidate_bp

app.register_blueprint(candidate_bp)


# ============================================================
# 基本設定
# ============================================================

VERSION = "1.1"

TARGET = 1_000_000

MAX_STEPS = 20

MAX_CAMPAIGN_CYCLES = 10


# ============================================================
# 対応戦略
#
# balanced を追加
# ============================================================

VALID_STRATEGIES = {
    "random",
    "safe",
    "balanced",
    "aggressive"
}


# ============================================================
# strategy_engine.py 側に balanced がまだ無い場合でも
# app.py の表示で落ちないようにする。
#
# ただし、本来は strategy_engine.py の
# STRATEGY_LABELS にも balanced を追加する。
# ============================================================

DISPLAY_STRATEGY_LABELS = {
    "random": STRATEGY_LABELS.get(
        "random",
        "ランダム"
    ),

    "safe": STRATEGY_LABELS.get(
        "safe",
        "セーフ"
    ),

    "balanced": STRATEGY_LABELS.get(
        "balanced",
        "バランス"
    ),

    "aggressive": STRATEGY_LABELS.get(
        "aggressive",
        "アグレッシブ"
    )
}


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return "Warashibe AI v1.1"


# ============================================================
# DOCS
# ============================================================

@app.route("/docs")
def docs():

    return """
    <!doctype html>

    <html lang="ja">

    <head>

        <meta charset="utf-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1">

        <title>
            Warashibe AI v1.1 API
        </title>

        <style>

            body {
                max-width: 850px;
                margin: 40px auto;
                padding: 20px;
                font-family: sans-serif;
                line-height: 1.7;
            }

            h1 {
                margin-bottom: 30px;
            }

            ul {
                line-height: 2.2;
            }

            a {
                font-size: 18px;
            }

            .post {
                color: #c62828;
                font-weight: bold;
            }

            .section {
                margin-top: 30px;
                padding: 20px;
                background: #f5f5f5;
                border-radius: 10px;
            }

        </style>

    </head>

    <body>

        <h1>
            Warashibe AI v1.1 API
        </h1>

        <h2>
            対応戦略
        </h2>

        <ul>

            <li>random：ランダム</li>

            <li>safe：セーフ</li>

            <li>balanced：バランス</li>

            <li>aggressive：アグレッシブ</li>

        </ul>

        <h2>
            API
        </h2>

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
                ：1回のわらしべ挑戦
            </li>

            <li>
                <a href="/simulate?strategy=random">
                    /simulate
                </a>
                ：単体シミュレーション
            </li>

            <li>
                <a href="/campaign/simulate?strategy=balanced&campaigns=1000&max_cycles=10">
                    /campaign/simulate
                </a>
                ：再挑戦ありの統計
            </li>

            <li>
                <a href="/strategy/recommendation">
                    /strategy/recommendation
                </a>
                ：AI戦略本部JSON
            </li>

            <li>
                <a href="/candidates/test">
                    /candidates/test
                </a>
                ：候補商品フィルターのテスト
            </li>

            <li>
                <a href="/candidate-form">
                    /candidate-form
                </a>
                ：ブラウザから候補商品を評価
            </li>

            <li>
                <a href="/capital-filter/test">
                    /capital-filter/test
                </a>
                ：現在資本に適合する候補商品を確認
            </li>

            <li>
                <a href="/candidates/pipeline-test">
                    /candidates/pipeline-test
                </a>
                ：候補商品選定パイプラインの統合テスト
            </li>

            <li>
                <strong class="post">
                    POST /candidates/evaluate
                </strong>
                ：候補商品を1件評価
            </li>

        </ul>

        <div class="section">

            <h2>
                v1.1 の流れ
            </h2>

            <p>
                仮想市場
                ↓
                戦略シミュレーション
                ↓
                AI戦略本部
            </p>

            <p>
                候補商品
                ↓
                危険フィルター
                ↓
                資本フィルター
                ↓
                ランキング
                ↓
                BEST CANDIDATE
            </p>

        </div>

    </body>

    </html>
    """


# ============================================================
# 共通関数
# ============================================================

def get_strategy():

    strategy = request.args.get(
        "strategy",
        "random"
    ).strip().lower()

    if strategy not in VALID_STRATEGIES:

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

@app.route("/journey")
def journey():

    strategy = get_strategy()

    if strategy is None:

        return strategy_error()

    result = run_cycle(
        strategy
    )

    return jsonify({

        "version":
            VERSION,

        "policy_version":
            POLICY_VERSION,

        "strategy":
            strategy,

        "start_capital":
            START_CAPITAL,

        "target":
            TARGET,

        **result

    })


# ============================================================
# /simulate
#
# 単体シミュレーション
# ============================================================

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

        result = run_cycle(
            strategy
        )

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

            stats = item_stats[
                item_name
            ]

            stats["attempts"] += 1

            if trade.get("success"):

                stats["successes"] += 1

            else:

                stats["failures"] += 1

        if result.get(
            "status"
        ) == "goal_reached":

            goal_reached += 1

    for stats in item_stats.values():

        attempts = stats["attempts"]

        if attempts:

            stats[
                "success_rate_percent"
            ] = round(
                stats["successes"]
                / attempts
                * 100,
                2
            )

        else:

            stats[
                "success_rate_percent"
            ] = 0

    return jsonify({

        "version":
            VERSION,

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

        "version":
            VERSION,

        "policy_version":
            POLICY_VERSION,

        "start_capital":
            START_CAPITAL,

        "target":
            TARGET,

        **summary

    })


# ============================================================
# /strategy/recommendation
#
# 4戦略を比較
# ============================================================

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

    strategy_results = []

    for strategy in (
        "random",
        "safe",
        "balanced",
        "aggressive"
    ):

        strategy_results.append(
            summarize_campaigns(
                strategy,
                campaigns,
                max_cycles
            )
        )

    recommendation = create_recommendation(
        strategy_results
    )

    return jsonify({

        "version":
            VERSION,

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


# ============================================================
# /strategy/report
#
# 人間向け戦略レポート
# ============================================================

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

    strategy_results = [

        summarize_campaigns(
            strategy,
            campaigns,
            max_cycles
        )

        for strategy in (
            "random",
            "safe",
            "balanced",
            "aggressive"
        )

    ]

    ranked_results = sorted(
        strategy_results,

        key=lambda result: (
            -result.get(
                "campaign_goal_rate_percent",
                0
            ),

            result.get(
                "average_cycles_used",
                float("inf")
            ),

            result.get(
                "total_restarts",
                float("inf")
            )
        )
    )

    recommendation = create_recommendation(
        strategy_results
    )

    return render_template_string(
        """
        <!doctype html>

        <html lang="ja">

        <head>

            <meta charset="utf-8">

            <meta name="viewport"
                  content="width=device-width, initial-scale=1">

            <title>
                Warashibe AI 戦略レポート
            </title>

            <style>

                body {
                    max-width: 850px;
                    margin: 40px auto;
                    padding: 20px;
                    font-family: sans-serif;
                    line-height: 1.7;
                }

                .card {
                    margin: 20px 0;
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
                            result.campaign_goal_rate_percent
                            }}%
                        </td>

                        <td>
                            {{
                            result.average_cycles_used
                            }}
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

        strategy_labels=DISPLAY_STRATEGY_LABELS
    )


# ============================================================
# /candidates/test
#
# 危険フィルター単体テスト
# ============================================================

# ============================================================
# START
#
# Render / Gunicorn では
#     gunicorn app:app
#
# が app オブジェクトを直接読み込むため、
# app.run() はローカル実行時だけ使用。
# ============================================================

if __name__ == "__main__":

    import os

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
