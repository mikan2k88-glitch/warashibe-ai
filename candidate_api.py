# ============================================================
# Warashibe AI v1.1
# candidate_api.py
#
# 役割：
# ・候補商品API
# ・候補商品フィルターテスト
# ・候補商品入力フォーム
#
# Flask本体：
# ・app.py
# ============================================================

from flask import Blueprint, jsonify, request, render_template_string

from candidate_engine import create_candidate
from danger_filter import filter_candidates
from capital_filter import filter_by_capital
from ranking_engine import rank_candidates
from candidate_pipeline import evaluate_candidates


VERSION = "1.1"

candidate_bp = Blueprint("candidate", __name__)


@candidate_bp.route("/candidates/test")
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

    ranked_candidates = rank_candidates(
        allowed
    )

    best_candidate = None

    if ranked_candidates:

        best_candidate = ranked_candidates[0]

    return jsonify({

        "version":
            VERSION,

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
# ============================================================

@candidate_bp.route("/capital-filter/test")
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

        "version":
            VERSION,

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
# /candidates/pipeline-test
# ============================================================

@candidate_bp.route("/candidates/pipeline-test")
def candidates_pipeline_test():

    current_capital = 10_000

    candidates = [

        create_candidate(
            name="安全な中古カメラ",
            purchase_price=8_000,
            expected_sale_price=12_000,
            source="test",
            category="camera",
            confidence=0.90
        ),

        create_candidate(
            name="資本オーバー高利益商品",
            purchase_price=15_000,
            expected_sale_price=30_000,
            source="test",
            category="brand",
            confidence=0.90
        ),

        create_candidate(
            name="低利益商品",
            purchase_price=8_000,
            expected_sale_price=8_200,
            source="test",
            category="misc",
            confidence=0.90
        ),

        create_candidate(
            name="情報不足商品",
            purchase_price=8_000,
            expected_sale_price=16_000,
            source="test",
            category="misc",
            confidence=0.30
        )

    ]

    result = evaluate_candidates(
        candidates,
        current_capital
    )

    return jsonify({

        "version":
            VERSION,

        "pipeline":
            "danger_filter -> "
            "capital_filter -> "
            "ranking_engine",

        **result

    })


# ============================================================
# /candidate-form
# ============================================================

@candidate_bp.route(
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

                purchase_price=
                    purchase_price,

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

                result = {

                    "status":
                        "allowed",

                    "candidate":
                        allowed[0]

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

        except (
            ValueError,
            TypeError
        ) as e:

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

            <meta name="viewport"
                  content="width=device-width, initial-scale=1">

            <title>
                Warashibe AI 候補商品評価
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
                    border-left: 6px solid #2e7d32;
                }

                .blocked {
                    background: #ffebee;
                    border-left: 6px solid #c62828;
                }

                .error {
                    background: #fff3e0;
                    border-left: 6px solid #ef6c00;
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
                AI地雷フィルターで評価します。
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
                            ALLOWED
                        </h2>

                        <p>
                            この候補商品は
                            地雷フィルターを通過しました。
                        </p>

                        <pre>
{{ result | tojson(indent=2) }}
                        </pre>

                    </div>

                {% elif result.status == "blocked" %}

                    <div class="result blocked">

                        <h2>
                            BLOCKED
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
                            ERROR
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

@candidate_bp.route(
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

    except (
        ValueError,
        TypeError
    ) as e:

        return jsonify({

            "error":
                f"候補商品のデータが不正です: {e}"

        }), 400

    allowed, blocked = filter_candidates(
        [candidate]
    )

    if allowed:

        return jsonify({

            "version":
                VERSION,

            "status":
                "allowed",

            "candidate":
                allowed[0]

        })

    return jsonify({

        "version":
            VERSION,

        "status":
            "blocked",

        "candidate":
            candidate,

        "reasons":
            blocked[0]["reasons"]

    })


