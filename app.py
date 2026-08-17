from flask import Flask, jsonify, request
import random

from market_engine import MARKET, find_items
from policy_engine import POLICY_VERSION, START_CAPITAL, evaluate_trade
from strategy_engine import create_recommendation

app = Flask(__name__)

TARGET = 1_000_000
MAX_STEPS = 20
MAX_CAMPAIGN_CYCLES = 10


@app.route("/")
def home():
    return "Warashibe AI v0.9"


@app.route("/docs")
def docs():
    return """
    <h1>Warashibe AI v0.9 API</h1>
    <ul>
        <li><a href="/journey?strategy=random">/journey</a>：1回の取引</li>
        <li><a href="/simulate?strategy=random">/simulate</a>：1サイクルの統計</li>
        <li><a href="/campaign/simulate?strategy=random">/campaign/simulate</a>：再挑戦ありの統計</li>
        <li><a href="/strategy/recommendation">/strategy/recommendation</a>：AI戦略本部の提案</li>
    </ul>
    """


def get_strategy():
    strategy = request.args.get("strategy", "random").lower()

    if strategy not in {"random", "safe", "aggressive"}:
        return None

    return strategy


def get_bounded_int(name, default, minimum, maximum):
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
        return max(items, key=lambda item: item["success_rate"])

    if strategy == "aggressive":
        return max(items, key=lambda item: item["next_value"])

    return random.choice(items)


def get_policy_allowed_items(capital):
    allowed_items = []
    blocked_items = []

    for item in find_items(capital):
        decision = evaluate_trade(capital, item)

        if decision["allowed"]:
            allowed_items.append(item)
        else:
            blocked_items.append({
                "item": item["name"],
                "reasons": decision["reasons"]
            })

    return allowed_items, blocked_items


def run_cycle(strategy):
    """100円から開始する、1回分のわらしべサイクル"""
    capital = START_CAPITAL
    history = []

    for step in range(1, MAX_STEPS + 1):
        available_items, blocked_items = get_policy_allowed_items(capital)

        if not available_items:
            return {
                "status": "policy_blocked",
                "final_capital": capital,
                "steps": step - 1,
                "history": history,
                "blocked_items": blocked_items
            }

        item = select_item(available_items, strategy)
        success = random.random() < item["success_rate"]

        trade = {
            "step": step,
            "capital_before": capital,
            "selected_item": item["name"],
            "price": item["price"],
            "next_value": item["next_value"],
            "success_rate": item["success_rate"],
            "success": success,
            "policy": evaluate_trade(capital, item)
        }

        if success:
            capital = item["next_value"]
            trade["capital_after"] = capital
            history.append(trade)

            if capital >= TARGET:
                return {
                    "status": "goal_reached",
                    "final_capital": capital,
                    "steps": step,
                    "history": history
                }

        else:
            trade["capital_after"] = 0
            trade["failure_reason"] = "trade_failed"
            history.append(trade)

            return {
                "status": "failed",
                "final_capital": 0,
                "steps": step,
                "history": history,
                "failure_reason": "trade_failed"
            }

    return {
        "status": "max_steps_reached",
        "final_capital": capital,
        "steps": MAX_STEPS,
        "history": history
    }


def run_campaign(strategy, max_cycles):
    """
    失敗したら100円から新サイクルを開始する。
    policy_blocked は同じ条件で再開しても解決しないため、その場で終了する。
    """
    failure_reasons = {}

    for cycle_number in range(1, max_cycles + 1):
        result = run_cycle(strategy)

        if result["status"] == "goal_reached":
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

        reason = result.get("failure_reason", result["status"])
        failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

        if result["status"] == "policy_blocked":
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


def summarize_campaigns(strategy, campaigns, max_cycles):
    goal_reached = 0
    total_cycles_used = 0
    total_restarts = 0
    failure_reasons = {}
    successful_route_summary = {}

    for _ in range(campaigns):
        result = run_campaign(strategy, max_cycles)

        total_cycles_used += result["cycles_used"]
        total_restarts += result["restarts"]

        for reason, count in result["failure_reasons"].items():
            failure_reasons[reason] = (
                failure_reasons.get(reason, 0) + count
            )

        if result["status"] == "goal_reached":
            goal_reached += 1
            route = result["successful_route"]

            successful_route_summary[route] = (
                successful_route_summary.get(route, 0) + 1
            )

    sorted_routes = dict(
        sorted(
            successful_route_summary.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )

    dominant_route = next(iter(sorted_routes), None)

    return {
        "strategy": strategy,
        "campaigns": campaigns,
        "max_cycles_per_campaign": max_cycles,
        "campaign_goal_reached": goal_reached,
        "campaign_goal_rate_percent": round(
            goal_reached / campaigns * 100, 2
        ),
        "average_cycles_used": round(
            total_cycles_used / campaigns, 2
        ),
        "total_restarts": total_restarts,
        "average_restarts": round(
            total_restarts / campaigns, 2
        ),
        "virtual_restart_contribution": total_restarts * START_CAPITAL,
        "failure_reasons": failure_reasons,
        "dominant_successful_route": dominant_route,
        "successful_route_summary": sorted_routes
    }


@app.route("/journey")
def journey():
    strategy = get_strategy()

    if strategy is None:
        return jsonify({"error": "strategy が不正です。"}), 400

    result = run_cycle(strategy)

    return jsonify({
        "version": "0.9",
        "policy_version": POLICY_VERSION,
        "strategy": strategy,
        "start_capital": START_CAPITAL,
        **result
    })


@app.route("/simulate")
def simulate():
    strategy = get_strategy()
    simulations = get_bounded_int("simulations", 10_000, 1, 100_000)

    if strategy is None:
        return jsonify({"error": "strategy が不正です。"}), 400

    if simulations is None:
        return jsonify({"error": "simulations は 1〜100000 の整数です。"}), 400

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
            stats = item_stats[trade["selected_item"]]
            stats["attempts"] += 1

            if trade["success"]:
                stats["successes"] += 1
            else:
                stats["failures"] += 1

        if result["status"] == "goal_reached":
            goal_reached += 1

    for stats in item_stats.values():
        attempts = stats["attempts"]
        stats["success_rate_percent"] = round(
            stats["successes"] / attempts * 100, 2
        ) if attempts else 0

    return jsonify({
        "version": "0.9",
        "policy_version": POLICY_VERSION,
        "strategy": strategy,
        "simulations": simulations,
        "goal_reached": goal_reached,
        "goal_rate_percent": round(goal_reached / simulations * 100, 2),
        "item_stats": item_stats
    })


@app.route("/campaign/simulate")
def campaign_simulate():
    strategy = get_strategy()
    campaigns = get_bounded_int("campaigns", 1_000, 1, 10_000)
    max_cycles = get_bounded_int(
        "max_cycles",
        MAX_CAMPAIGN_CYCLES,
        1,
        100
    )

    if strategy is None:
        return jsonify({"error": "strategy が不正です。"}), 400

    if campaigns is None or max_cycles is None:
        return jsonify({
            "error": "campaigns は1〜10000、max_cyclesは1〜100で指定してください。"
        }), 400

    summary = summarize_campaigns(strategy, campaigns, max_cycles)

    return jsonify({
        "version": "0.9",
        "policy_version": POLICY_VERSION,
        "start_capital": START_CAPITAL,
        "target": TARGET,
        **summary
    })


@app.route("/strategy/recommendation")
def strategy_recommendation():
    """
    AI戦略本部。
    3戦略を同じ試行回数・再挑戦回数で比較し、人間への提案を返す。
    """
    campaigns = get_bounded_int("campaigns", 1_000, 100, 10_000)
    max_cycles = get_bounded_int(
        "max_cycles",
        MAX_CAMPAIGN_CYCLES,
        1,
        100
    )

    if campaigns is None or max_cycles is None:
        return jsonify({
            "error": "campaigns は100〜10000、max_cyclesは1〜100で指定してください。"
        }), 400

    strategy_results = [
        summarize_campaigns(strategy, campaigns, max_cycles)
        for strategy in ("random", "safe", "aggressive")
    ]

    recommendation = create_recommendation(strategy_results)

    return jsonify({
        "version": "0.9",
        "policy_version": POLICY_VERSION,
        "mode": "virtual_market_only",
        "current_capital": START_CAPITAL,
        "target": TARGET,
        "strategies": strategy_results,
        "recommendation": recommendation
    })


if __name__ == "__main__":
    app.run(debug=True)
