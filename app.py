from flask import Flask




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
from strategy_api import strategy_bp

app.register_blueprint(candidate_bp)
app.register_blueprint(strategy_bp)


# ============================================================
# 基本設定
# ============================================================

VERSION = "1.1"



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
