from flask import Flask, jsonify, request
import random

from market_engine import MARKET, find_items
from policy_engine import POLICY_VERSION, START_CAPITAL, evaluate_trade

app = Flask(__name__)

TARGET = 1_000_000
MAX_STEPS = 20
SUCCESSFUL_ROUTES_LIMIT = 100
MAX_CAMPAIGN_CYCLES = 10


@app.route("/")
def home():
    return "Warashibe AI v0.8"


@app.route("/docs")
def docs():
    return """
    <h1>Warashibe AI v0.8 API</h1>
    <ul>
        <li><a href="/journey?strategy=random">/journey</a>：1回のわらしべ取引</li>
        <li><a href="/simulate?strategy=random">/simulate</a>：1サイクルの統計</li>
        <li><a href="/campaign/simulate?strategy=random">/campaign/simulate</a>：失敗時に100円から再開する統計</li>
    </ul>
    <p>strategy: random / safe / aggressive</p>
    """


def build_capital_bands():
    prices = sorted({item["price"] for item in MARKET})
    bands = {}

    for index, price in enumerate(prices):
        if index < len(prices) - 1:
            bands[price] = f"{price:,}-{prices[index + 1] - 1:,}"
        else:
            bands[price] = f"{price:,}+"

    return bands


CAPITAL_BANDS = build_capital_bands()


def get_strategy():
    strategy = request.args.get("strategy", "random").lower()

    if strategy not in {"random", "safe", "aggressive"}:
        return None

    return strategy


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
    """100円から始める、1回分のわらしべサイクル"""
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


@app.route("/journey")
def journey():
    strategy = get_strategy()

    if strategy is None:
        return jsonify({"error": "strategy が不正です。"}), 400

    result = run_cycle(strategy)

    return jsonify({
        "version": "0.8",
        "policy_version": POLICY_VERSION,
        "strategy": strategy,
        "start_capital": START_CAPITAL,
        **result
    })


@app.route("/simulate")
def simulate():
    strategy = get_strategy()

    if strategy is None:
        return jsonify({"error": "strategy が不正です。"}), 400

    simulations = 10_000
    goal_reached = 0
    failure_step_stats = {str(step): 0 for step in range(1, MAX_STEPS + 1)}
    item_stats = {
        item["name"]: {"attempts": 0, "successes": 0, "failures": 0}
        for item in MARKET
    }
    successful_route_summary = {}

    for _ in range(simulations):
        result = run_cycle(strategy)
        history = result["history"]

        for trade in history:
            stats = item_stats[trade["selected_item"]]
            stats["attempts"] += 1

            if trade["success"]:
                stats["successes"] += 1
            else:
                stats["failures"] += 1
                failure_step_stats[str(trade["step"])] += 1

        if result["status"] == "goal_reached":
            goal_reached += 1
            route = " → ".join(
                trade["selected_item"]
                for trade in history
            )
            successful_route_summary[route] = (
                successful_route_summary.get(route, 0) + 1
            )

    for stats in item_stats.values():
        attempts = stats["attempts"]
        stats["success_rate_percent"] = round(
            stats["successes"] / attempts * 100, 2
        ) if attempts else 0

    return jsonify({
        "version": "0.8",
        "policy_version": POLICY_VERSION,
        "strategy": strategy,
        "simulations": simulations,
        "start_capital": START_CAPITAL,
        "target": TARGET,
        "goal_reached": goal_reached,
        "goal_rate_percent": round(goal_reached / simulations * 100, 2),
        "item_stats": item_stats,
        "failure_step_stats": failure_step_stats,
        "successful_route_summary": dict(
            sorted(
                successful_route_summary.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )
    })


@app.route("/campaign/simulate")
def campaign_simulate():
    """
    失敗したら100円から新しいサイクルを開始する。
    1キャンペーンにつき最大10サイクル。
    """
    strategy = get_strategy()

    if strategy is None:
        return jsonify({"error": "strategy が不正です。"}), 400

    campaigns = 1_000
    campaign_goal_reached = 0
    total_cycles_used = 0
    total_restarts = 0
    failure_reasons = {}
    successful_routes = {}

    for _ in range(campaigns):
        cycles_used = 0
        reached_goal = False

        for _ in range(MAX_CAMPAIGN_CYCLES):
            cycles_used += 1
            result = run_cycle(strategy)

            if result["status"] == "goal_reached":
                reached_goal = True
                campaign_goal_reached += 1

                route = " → ".join(
                    trade["selected_item"]
                    for trade in result["history"]
                )
                successful_routes[route] = (
                    successful_routes.get(route, 0) + 1
                )
                break

            reason = result.get("failure_reason", result["status"])
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

        total_cycles_used += cycles_used
        total_restarts += max(0, cycles_used - 1)

    return jsonify({
        "version": "0.8",
        "policy_version": POLICY_VERSION,
        "strategy": strategy,
        "campaigns": campaigns,
        "max_cycles_per_campaign": MAX_CAMPAIGN_CYCLES,
        "campaign_goal_reached": campaign_goal_reached,
        "campaign_goal_rate_percent": round(
            campaign_goal_reached / campaigns * 100, 2
        ),
        "average_cycles_used": round(total_cycles_used / campaigns, 2),
        "total_restarts": total_restarts,
        "virtual_restart_contribution": total_restarts * START_CAPITAL,
        "failure_reasons": failure_reasons,
        "successful_route_summary": dict(
            sorted(
                successful_routes.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )
    })


if __name__ == "__main__":
    app.run(debug=True)
