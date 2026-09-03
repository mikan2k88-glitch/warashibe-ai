from flask import Flask, request, jsonify, render_template_string

from market_engine import MARKET
from policy_engine import POLICY_VERSION, START_CAPITAL
from strategy_engine import STRATEGY_LABELS, create_recommendation
from simulation_engine import (
    run_cycle,
    summarize_campaigns,
    evaluate_strategies,
)
from candidate_engine import create_candidate
from danger_filter import filter_candidates
from capital_filter import filter_by_capital
from ranking_engine import rank_candidates
from candidate_pipeline import evaluate_candidates


app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({
        "name": "Warashibe AI",
        "version": "1.1",
        "status": "running",
        "policy_version": POLICY_VERSION,
        "start_capital": START_CAPITAL,
    })


@app.route("/docs")
def docs():
    return jsonify({
        "endpoints": [
            "/",
            "/journey",
            "/simulate",
            "/campaign/simulate",
            "/strategy/recommendation",
            "/strategy/report",
            "/strategy/auto",
            "/strategy/compare",
            "/candidates/test",
            "/capital-filter/test",
            "/candidates/pipeline-test",
            "/candidate-form",
            "/candidates/evaluate",
        ]
    })


@app.route("/journey")
def journey():
    strategy = request.args.get("strategy", "balanced")

    result = run_cycle(strategy=strategy)

    return jsonify(result)


@app.route("/simulate")
def simulate():
    strategy = request.args.get("strategy", "balanced")

    try:
        simulations = int(request.args.get("simulations", 1000))
    except ValueError:
        simulations = 1000

    simulations = max(1, min(simulations, 10000))

    successes = 0
    failures = 0
    max_capitals = []
    steps_list = []

    for _ in range(simulations):
        result = run_cycle(strategy=strategy)

        if result.get("status") == "goal_reached":
            successes += 1
        else:
            failures += 1

        max_capitals.append(result.get("max_capital", 0))
        steps_list.append(result.get("steps", 0))

    return jsonify({
        "strategy": strategy,
        "simulations": simulations,
        "successes": successes,
        "failures": failures,
        "goal_rate_percent": round(
            successes / simulations * 100,
            2
        ),
        "average_max_capital": round(
            sum(max_capitals) / simulations,
            2
        ),
        "average_steps": round(
            sum(steps_list) / simulations,
            2
        ),
    })


@app.route("/campaign/simulate")
def campaign_simulate():
    strategy = request.args.get("strategy", "balanced")

    try:
        campaigns = int(request.args.get("campaigns", 1000))
    except ValueError:
        campaigns = 1000

    try:
        max_cycles = int(request.args.get("max_cycles", 10))
    except ValueError:
        max_cycles = 10

    campaigns = max(1, min(campaigns, 10000))
    max_cycles = max(1, min(max_cycles, 100))

    result = summarize_campaigns(
        strategy=strategy,
        campaigns=campaigns,
        max_cycles=max_cycles,
    )

    return jsonify(result)


@app.route("/strategy/recommendation")
def strategy_recommendation():
    strategy = request.args.get("strategy", "balanced")

    result = create_recommendation(strategy)

    return jsonify(result)


@app.route("/strategy/report")
def strategy_report():
    reports = {}

    for strategy in STRATEGY_LABELS:
        reports[strategy] = create_recommendation(strategy)

    return jsonify({
        "policy_version": POLICY_VERSION,
        "strategies": reports,
    })


@app.route("/strategy/compare")
def strategy_compare():
    try:
        campaigns = int(request.args.get("campaigns", 1000))
    except ValueError:
        campaigns = 1000

    try:
        max_cycles = int(request.args.get("max_cycles", 10))
    except ValueError:
        max_cycles = 10

    campaigns = max(1, min(campaigns, 10000))
    max_cycles = max(1, min(max_cycles, 100))

    strategy_results, ranked_results = evaluate_strategies(
        campaigns=campaigns,
        max_cycles=max_cycles,
    )

    return jsonify({
        "campaigns": campaigns,
        "max_cycles_per_campaign": max_cycles,
        "policy_version": POLICY_VERSION,
        "strategies": strategy_results,
        "ranking": ranked_results,
    })


@app.route("/strategy/auto")
def strategy_auto():
    try:
        campaigns = int(request.args.get("campaigns", 1000))
    except ValueError:
        campaigns = 1000

    try:
        max_cycles = int(request.args.get("max_cycles", 10))
    except ValueError:
        max_cycles = 10

    campaigns = max(1, min(campaigns, 10000))
    max_cycles = max(1, min(max_cycles, 100))

    strategy_results, ranked_results = evaluate_strategies(
        campaigns=campaigns,
        max_cycles=max_cycles,
    )

    if not ranked_results:
        return jsonify({
            "status": "error",
            "message": "戦略評価結果が取得できませんでした。",
        }), 500

    best = ranked_results[0]
    best_strategy = best.get("strategy")

    return jsonify({
        "status": "success",
        "selected_strategy": best_strategy,
        "selected_strategy_label": STRATEGY_LABELS.get(
            best_strategy,
            best_strategy,
        ),
        "reason": "全戦略を同一条件でシミュレーションし、総合ランキング1位を自動選択しました。",
        "campaigns": campaigns,
        "max_cycles_per_campaign": max_cycles,
        "policy_version": POLICY_VERSION,
        "selected_result": strategy_results.get(
            best_strategy,
            {},
        ),
        "ranking": ranked_results,
        "all_results": strategy_results,
    })


@app.route("/candidates/test")
def candidates_test():
    candidates = [
        {
            "name": item["name"],
            "price": item["price"],
            "success_rate": item["success_rate"],
            "next_value": item["next_value"],
        }
        for item in MARKET
    ]

    filtered = filter_candidates(candidates)

    return jsonify({
        "candidates": candidates,
        "filtered": filtered,
    })


@app.route("/capital-filter/test")
def capital_filter_test():
    capital = request.args.get("capital", START_CAPITAL)

    try:
        capital = int(capital)
    except ValueError:
        capital = START_CAPITAL

    candidates = [
        {
            "name": item["name"],
            "price": item["price"],
            "success_rate": item["success_rate"],
            "next_value": item["next_value"],
        }
        for item in MARKET
    ]

    filtered = capital_filter(candidates, capital)

    return jsonify({
        "capital": capital,
        "candidates": filtered,
    })


@app.route("/candidates/pipeline-test")
def candidates_pipeline_test():
    capital = request.args.get("capital", START_CAPITAL)

    try:
        capital = int(capital)
    except ValueError:
        capital = START_CAPITAL

    candidates = [
        {
            "name": item["name"],
            "price": item["price"],
            "success_rate": item["success_rate"],
            "next_value": item["next_value"],
        }
        for item in MARKET
    ]

    result = evaluate_candidates(
        candidates=candidates,
        capital=capital,
    )

    return jsonify(result)


@app.route("/candidate-form")
def candidate_form():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>Warashibe AI Candidate Test</title>
    </head>
    <body>
        <h1>Warashibe AI Candidate Test</h1>

        <form method="post" action="/candidates/evaluate">
            <label>
                商品名：
                <input type="text" name="name" required>
            </label>
            <br><br>

            <label>
                価格：
                <input type="number" name="price" required>
            </label>
            <br><br>

            <label>
                成功率：
                <input
                    type="number"
                    name="success_rate"
                    step="0.01"
                    min="0"
                    max="1"
                    required
                >
            </label>
            <br><br>

            <label>
                次の価値：
                <input type="number" name="next_value" required>
            </label>
            <br><br>

            <button type="submit">評価する</button>
        </form>
    </body>
    </html>
    """)


@app.route("/candidates/evaluate", methods=["POST"])
def candidates_evaluate():
    try:
        name = request.form.get("name", "")
        price = int(request.form.get("price", 0))
        success_rate = float(
            request.form.get("success_rate", 0)
        )
        next_value = int(
            request.form.get("next_value", 0)
        )
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "入力値が不正です。",
        }), 400

    candidate = create_candidate(
        name=name,
        price=price,
        success_rate=success_rate,
        next_value=next_value,
    )

    return jsonify(candidate)


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port,
    )
