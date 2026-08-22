from flask import Flask, jsonify, request, render_template_string

from market_engine import MARKET
from policy_engine import POLICY_VERSION, START_CAPITAL
from strategy_engine import STRATEGY_LABELS, create_recommendation

from simulation_engine import (
    TARGET,
    MAX_CAMPAIGN_CYCLES,
    run_cycle,
    summarize_campaigns
)

from candidate_engine import create_candidate
from danger_filter import filter_candidates
from ranking_engine import rank_candidates
from capital_filter import filter_by_capital
from candidate_ranker import (
    rank_candidates,
    get_best_candidate
)


# ============================================================
# Warashibe AI v1.1
#
# AI戦略本部
# 仮想市場
# 候補商品地雷フィルター
# 候補商品ランキング
# ============================================================

app = Flask(__name__)


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

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1"
        >

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

                ：単体シミュレーション

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

                ：AI戦略本部JSON

            </li>

            <li>

                <a href="/candidates/test">
                    /candidates/test
                </a>

                ：候補商品フィルター＋ランキングテスト

            </li>

<li>
    <a href="/capital-filter/test">
        /capital-filter/test
    </a>
    ：現在資本に適合する候補商品を確認
</li>

            <li>

                <a href="/candidate-form">
                    /candidate-form
                </a>

                ：ブラウザから候補商品を評価

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

                ↓

                候補商品

                ↓

                地雷フィルター

                ↓

                採用候補

                ↓

                候補商品ランキング

                ↓

                最有力候補

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

    except (ValueError, TypeError):

        return None

    if minimum <= value <= maximum:

        return value

    return None


# ============================================================
# AI戦略比較
# ============================================================

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


# ============================================================
# /journey
# ============================================================

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

        "version":
            "1.1",

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
            "1.1",

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
                "max_cycles は1〜100で指定してください。"

        }), 400


    summary = summarize_campaigns(

        strategy,
        campaigns,
        max_cycles
    )


    return jsonify({

        "version":
            "1.1",

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


    if (

        campaigns is None
        or max_cycles is None

    ):

        return jsonify({

            "error":

                "campaigns は100〜10000、"
                "max_cycles は1〜100で指定してください。"

        }), 400


    strategy_results, _, recommendation = (

        evaluate_strategies(

            campaigns,
            max_cycles
        )
    )


    return jsonify({

        "version":
            "1.1",

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

            <meta
                name="viewport"
                content="width=device-width, initial-scale=1"
            >

            <title>
                Warashibe AI 戦略レポート
            </title>

            <style>

                body {
                    max-width: 800px;
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
                Warashibe AI
                戦略レポート
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

                    {{
                    recommendation.reason
                    }}

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


# ============================================================
# /candidates/test
#
# 固定テスト商品
# 地雷フィルター
# 候補ランキング
# ============================================================

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


    # --------------------------------------------------------
    # 地雷フィルター
    # --------------------------------------------------------

    allowed, blocked = filter_candidates(
        candidates
    )


    # --------------------------------------------------------
    # 候補商品ランキング
    # --------------------------------------------------------

    ranked_candidates = rank_candidates(
        allowed
    )


    best_candidate = get_best_candidate(
        allowed
    )


    return jsonify({

        "version":
            "1.1",

        "total_candidates":
            len(candidates),

        "allowed_count":
            len(allowed),

        "blocked_count":
            len(blocked),

        "allowed":
            allowed,

        "blocked":
            blocked,

        "ranked_candidates":
            ranked_candidates,

        "best_candidate":
            best_candidate
    })

# ============================================================
# /capital-filter/test
# 現在資本で購入可能な候補商品を確認
# ============================================================

@app.route("/capital-filter/test")
def capital_filter_test():

    current_capital = 10_000

    candidates = [

        create_candidate(
            name="資本内の商品",
            purchase_price=8_000,
            expected_sale_price=12_000,
            source="test",
            category="camera",
            confidence=0.90
        ),

        create_candidate(
            name="資本ぴったりの商品",
            purchase_price=10_000,
            expected_sale_price=15_000,
            source="test",
            category="electronics",
            confidence=0.90
        ),

        create_candidate(
            name="資本オーバーの商品",
            purchase_price=15_000,
            expected_sale_price=25_000,
            source="test",
            category="brand",
            confidence=0.90
        ),

        create_candidate(
            name="高額すぎる商品",
            purchase_price=100_000,
            expected_sale_price=150_000,
            source="test",
            category="misc",
            confidence=0.90
        )
    ]

    allowed, blocked = filter_by_capital(
        candidates,
        current_capital
    )

    return jsonify({

        "version": "1.1",

        "current_capital":
            current_capital,

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


# ============================================================
# /candidate-form
#
# ブラウザから候補商品を評価
# ============================================================

@app.route(
    "/candidate-form",
    methods=["GET", "POST"]
)
def candidate_form():

    result = None


    if request.method == "POST":

        try:

            name = request.form.get(
                "name",
                ""
            ).strip()


            purchase_price = float(

                request.form.get(
                    "purchase_price",
                    0
                )
            )


            expected_sale_price = float(

                request.form.get(
                    "expected_sale_price",
                    0
                )
            )


            confidence = float(

                request.form.get(
                    "confidence",
                    0
                )
            )


            source = request.form.get(
                "source",
                "manual"
            )


            category = request.form.get(
                "category",
                "misc"
            )


            if not name:

                raise ValueError(
                    "商品名を入力してください。"
                )


            if purchase_price < 0:

                raise ValueError(
                    "仕入れ価格は0以上で入力してください。"
                )


            if expected_sale_price < 0:

                raise ValueError(
                    "想定売却価格は0以上で入力してください。"
                )


            if not 0 <= confidence <= 1:

                raise ValueError(
                    "情報信頼度は0.0〜1.0で入力してください。"
                )


            candidate = create_candidate(

                name=name,

                purchase_price=purchase_price,

                expected_sale_price=
                    expected_sale_price,

                source=source,

                category=category,

                confidence=confidence
            )


            allowed, blocked = filter_candidates(
                [candidate]
            )


            if allowed:

                ranked_candidates = rank_candidates(
                    allowed
                )

                best_candidate = get_best_candidate(
                    allowed
                )

                result = {

                    "status":
                        "allowed",

                    "candidate":
                        allowed[0],

                    "ranked_candidates":
                        ranked_candidates,

                    "best_candidate":
                        best_candidate
                }

            else:

                result = {

                    "status":
                        "blocked",

                    "candidate":
                        candidate,

                    "reasons":
                        blocked[0]["reasons"]
                }


        except (ValueError, TypeError) as e:

            result = {

                "status":
                    "error",

                "message":
                    f"入力値が不正です: {e}"
            }


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
                Warashibe AI
                候補商品評価
            </title>


            <style>

                body {
                    max-width: 700px;
                    margin: 30px auto;
                    padding: 20px;
                    font-family: sans-serif;
                    line-height: 1.6;
                }

                h1 {
                    margin-bottom: 30px;
                }

                label {
                    display: block;
                    margin-top: 15px;
                    font-weight: bold;
                }

                input,
                select {
                    width: 100%;
                    box-sizing: border-box;
                    padding: 10px;
                    margin-top: 5px;
                    font-size: 16px;
                }

                button {
                    margin-top: 25px;
                    padding: 12px 25px;
                    font-size: 16px;
                    cursor: pointer;
                }

                .result {
                    margin-top: 30px;
                    padding: 20px;
                    border-radius: 10px;
                }

                .allowed {
                    background: #e8f5e9;
                    border-left:
                        6px solid #2e7d32;
                }

                .blocked {
                    background: #ffebee;
                    border-left:
                        6px solid #c62828;
                }

                .error {
                    background: #fff3e0;
                    border-left:
                        6px solid #ef6c00;
                }

                pre {
                    white-space: pre-wrap;
                    word-break: break-word;
                    background: #f5f5f5;
                    padding: 15px;
                    overflow-x: auto;
                }

            </style>

        </head>


        <body>

            <h1>

                Warashibe AI

                <br>

                候補商品評価

            </h1>


            <p>

                商品情報を入力すると、

                地雷フィルターと

                ランキングエンジンで評価します。

            </p>


            <form method="POST">


                <label>
                    商品名
                </label>

                <input

                    type="text"

                    name="name"

                    placeholder="例：中古カメラ"

                    required
                >


                <label>
                    仕入れ価格
                </label>

                <input

                    type="number"

                    name="purchase_price"

                    placeholder="10000"

                    min="0"

                    step="1"

                    required
                >


                <label>
                    想定売却価格
                </label>

                <input

                    type="number"

                    name="expected_sale_price"

                    placeholder="15000"

                    min="0"

                    step="1"

                    required
                >


                <label>
                    情報信頼度（0.0〜1.0）
                </label>

                <input

                    type="number"

                    name="confidence"

                    placeholder="0.9"

                    min="0"

                    max="1"

                    step="0.01"

                    required
                >


                <label>
                    カテゴリ
                </label>

                <select name="category">

                    <option value="camera">
                        カメラ
                    </option>

                    <option value="electronics">
                        電子機器
                    </option>

                    <option value="brand">
                        ブランド
                    </option>

                    <option value="book">
                        本・古書
                    </option>

                    <option value="game">
                        ゲーム
                    </option>

                    <option value="misc">
                        その他
                    </option>

                </select>


                <label>
                    情報源
                </label>

                <input

                    type="text"

                    name="source"

                    value="manual"
                >


                <button type="submit">

                    商品を評価する

                </button>

            </form>


            {% if result %}


                {% if result.status == "allowed" %}

                    <div class="result allowed">

                        <h2>
                            ✅ ALLOWED
                        </h2>

                        <p>

                            この候補商品は

                            地雷フィルターを通過しました。

                        </p>


                        <h3>
                            ランキング結果
                        </h3>

                        <p>

                            順位：

                            {{
                            result.best_candidate.rank
                            }}位

                        </p>


                        <p>

                            総合スコア：

                            {{
                            result.best_candidate.score
                            }}

                        </p>


                        <pre>
{{ result | tojson(indent=2) }}
                        </pre>

                    </div>


                {% elif result.status == "blocked" %}

                    <div class="result blocked">

                        <h2>
                            ❌ BLOCKED
                        </h2>

                        <p>

                            この商品は

                            地雷フィルターによって

                            除外されました。

                        </p>


                        <h3>
                            除外理由
                        </h3>


                        <ul>

                            {% for reason in result.reasons %}

                                <li>

                                    {{ reason }}

                                </li>

                            {% endfor %}

                        </ul>


                        <pre>
{{ result | tojson(indent=2) }}
                        </pre>

                    </div>


                {% else %}

                    <div class="result error">

                        <h2>
                            ⚠️ ERROR
                        </h2>

                        <p>

                            {{ result.message }}

                        </p>

                    </div>

                {% endif %}


            {% endif %}

        </body>

        </html>

        """,

        result=result
    )


# ============================================================
# POST /candidates/evaluate
#
# 外部JSONから候補商品を1件評価
# ============================================================

@app.route(
    "/candidates/evaluate",
    methods=["POST"]
)
def candidates_evaluate():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "error":
                "JSONデータを送信してください。"

        }), 400


    try:

        candidate = create_candidate(

            name=data.get(
                "name"
            ),

            purchase_price=data.get(
                "purchase_price",
                0
            ),

            expected_sale_price=data.get(
                "expected_sale_price",
                0
            ),

            source=data.get(
                "source",
                "unknown"
            ),

            category=data.get(
                "category",
                "unknown"
            ),

            confidence=data.get(
                "confidence",
                0
            ),

            metadata=data.get(
                "metadata",
                {}
            )
        )


    except (ValueError, TypeError) as e:

        return jsonify({

            "error":

                f"候補商品のデータが不正です: {e}"

        }), 400


    allowed, blocked = filter_candidates(
        [candidate]
    )


    if allowed:

        ranked_candidates = rank_candidates(
            allowed
        )

        best_candidate = get_best_candidate(
            allowed
        )


        return jsonify({

            "version":
                "1.1",

            "status":
                "allowed",

            "candidate":
                allowed[0],

            "ranked_candidates":
                ranked_candidates,

            "best_candidate":
                best_candidate
        })


    return jsonify({

        "version":
            "1.1",

        "status":
            "blocked",

        "candidate":
            candidate,

        "reasons":
            blocked[0]["reasons"]
    })


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=10000,

        debug=True
    )
