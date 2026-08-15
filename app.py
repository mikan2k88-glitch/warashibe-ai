from flask import Flask, jsonify, request
import random

from market_engine import MARKET, find_items

app = Flask(__name__)

TARGET = 1_000_000
START_CAPITAL = 100
MAX_STEPS = 20
SUCCESSFUL_ROUTES_LIMIT = 100


@app.route("/")
def home():
    return "Warashibe AI v0.7"


@app.route("/docs")
def docs():
    return """
    <h1>Warashibe AI v0.7 API</h1>
    <ul>
        <li><a href="/journey?strategy=random">/journey?strategy=random</a>：1回の交換</li>
        <li><a href="/simulate?strategy=random">/simulate?strategy=random</a>：ランダム選択で統計</li>
        <li><a href="/simulate?strategy=safe">/simulate?strategy=safe</a>：成功率優先で統計</li>
        <li><a href="/simulate?strategy=aggressive">/simulate?strategy=aggressive</a>：利益優先で統計</li>
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


def select_item(items, strategy):
    """選択戦略に応じて商品を1つ選ぶ"""

    if strategy == "safe":
        return max(items, key=lambda item: item["success_rate"])

    if strategy == "aggressive":
        return max(items, key=lambda item: item["next_value"])

    return random.choice(items)


def get_strategy():
    strategy = request.args.get("strategy", "random").lower()

    if strategy not in {"random", "safe", "aggressive"}:
        return None

    return strategy


def create_item_stats():
    return {
        item["name"]: {
            "attempts": 0,
            "successes": 0,
            "failures": 0
        }
        for item in MARKET
    }


@app.route("/journey")
def journey():
    strategy = get_strategy()

    if strategy is None:
        return jsonify({
            "error": "strategy は random, safe, aggressive のいずれかを指定してください。"
        }), 400

    capital = START_CAPITAL
    history = []

    for step in range(1, MAX_STEPS + 1):
        available_items = find_items(capital)

        if not available_items:
            return jsonify({
                "status": "stopped",
                "strategy": strategy,
                "final_capital": capital,
                "steps": step - 1,
                "history": history
            })

        item = select_item(available_items, strategy)
        success = random.random() < item["success_rate"]

        trade = {
            "step": step,
            "capital_before": capital,
            "available_choices": [
                {
                    "name": choice["name"],
                    "success_rate": choice["success_rate"],
                    "next_value": choice["next_value"]
                }
                for choice in available_items
            ],
            "selected_item": item["name"],
            "success": success
        }

        if success:
            capital = item["next_value"]
            trade["capital_after"] = capital
            history.append(trade)

            if capital >= TARGET:
                return jsonify({
                    "status": "goal_reached",
                    "strategy": strategy,
                    "final_capital": capital,
                    "steps": step,
                    "history": history
                })

        else:
            trade["capital_after"] = 0
            history.append(trade)

            return jsonify({
                "status": "failed",
                "strategy": strategy,
                "final_capital": 0,
                "steps": step,
                "history": history
            })

    return jsonify({
        "status": "max_steps_reached",
        "strategy": strategy,
        "final_capital": capital,
        "steps": MAX_STEPS,
        "history": history
    })


@app.route("/simulate")
def simulate():
    strategy = get_strategy()

    if strategy is None:
        return jsonify({
            "error": "strategy は random, safe, aggressive のいずれかを指定してください。"
        }), 400

    simulations = 10_000
    goal_reached = 0
    total_steps = 0
    total_max_capital = 0

    item_stats = create_item_stats()

    failure_step_stats = {
        str(step): 0
        for step in range(1, MAX_STEPS + 1)
    }

    capital_band_stats = {
        band: {
            "entries": 0,
            "successful_trades": 0,
            "failed_trades": 0
        }
        for band in CAPITAL_BANDS.values()
    }

    successful_routes = []
    successful_route_summary = {}

    for _ in range(simulations):
        capital = START_CAPITAL
        max_capital = capital
        steps = 0
        route = []

        for step in range(1, MAX_STEPS + 1):
            available_items = find_items(capital)

            if not available_items:
                break

            steps += 1
            item = select_item(available_items, strategy)
            item_name = item["name"]
            capital_band = CAPITAL_BANDS[capital]

            route.append(item_name)
            item_stats[item_name]["attempts"] += 1
            capital_band_stats[capital_band]["entries"] += 1

            success = random.random() < item["success_rate"]

            if success:
                item_stats[item_name]["successes"] += 1
                capital_band_stats[capital_band]["successful_trades"] += 1

                capital = item["next_value"]
                max_capital = max(max_capital, capital)

                if capital >= TARGET:
                    goal_reached += 1

                    route_text = " → ".join(route)
                    successful_route_summary[route_text] = (
                        successful_route_summary.get(route_text, 0) + 1
                    )

                    if len(successful_routes) < SUCCESSFUL_ROUTES_LIMIT:
                        successful_routes.append(route)

                    break

            else:
                item_stats[item_name]["failures"] += 1
                capital_band_stats[capital_band]["failed_trades"] += 1
                failure_step_stats[str(step)] += 1
                break

        total_steps += steps
        total_max_capital += max_capital

    for stats in item_stats.values():
        attempts = stats["attempts"]
        stats["success_rate_percent"] = round(
            stats["successes"] / attempts * 100, 2
        ) if attempts else 0

    for stats in capital_band_stats.values():
        entries = stats["entries"]
        stats["survival_rate_percent"] = round(
            stats["successful_trades"] / entries * 100, 2
        ) if entries else 0

    sorted_route_summary = dict(
        sorted(
            successful_route_summary.items(),
            key=lambda route: route[1],
            reverse=True
        )
    )

    return jsonify({
        "version": "0.7",
        "strategy": strategy,
        "simulations": simulations,
        "start_capital": START_CAPITAL,
        "target": TARGET,
        "goal_reached": goal_reached,
        "goal_rate_percent": round(goal_reached / simulations * 100, 2),
        "average_steps": round(total_steps / simulations, 2),
        "average_max_capital": round(total_max_capital / simulations, 2),

        "item_stats": item_stats,
        "failure_step_stats": failure_step_stats,
        "capital_band_stats": capital_band_stats,

        "successful_routes_count": goal_reached,
        "successful_routes_returned": len(successful_routes),
        "successful_routes": successful_routes,
        "successful_route_summary": sorted_route_summary
    })


if __name__ == "__main__":
    app.run(debug=True)
