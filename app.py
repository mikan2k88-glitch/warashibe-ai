from flask import Flask, jsonify
import random

from market_engine import MARKET, find_item

app = Flask(__name__)


@app.route("/")
def home():
    return "Warashibe AI v0.6"


def build_capital_bands():
    """MARKET の価格帯から資本帯ラベルを作る"""
    prices = [item["price"] for item in MARKET]
    bands = {}

    for index, price in enumerate(prices):
        if index < len(prices) - 1:
            next_price = prices[index + 1]
            label = f"{price:,}-{next_price - 1:,}"
        else:
            label = f"{price:,}+"

        bands[price] = label

    return bands


CAPITAL_BANDS = build_capital_bands()


@app.route("/journey")
def journey():
    capital = 100
    start_capital = capital
    history = []

    max_steps = 20
    target = 1_000_000

    for step in range(1, max_steps + 1):
        item = find_item(capital)

        if item is None:
            return jsonify({
                "status": "stopped",
                "start_capital": start_capital,
                "final_capital": capital,
                "steps": step - 1,
                "history": history
            })

        success = random.random() < item["success_rate"]

        trade = {
            "step": step,
            "capital_before": capital,
            "item": item["name"],
            "price": item["price"],
            "success": success
        }

        if success:
            capital = item["next_value"]
            trade["capital_after"] = capital
            history.append(trade)

            if capital >= target:
                return jsonify({
                    "status": "goal_reached",
                    "start_capital": start_capital,
                    "final_capital": capital,
                    "steps": step,
                    "history": history
                })

        else:
            capital = 0
            trade["capital_after"] = 0
            history.append(trade)

            return jsonify({
                "status": "failed",
                "start_capital": start_capital,
                "final_capital": 0,
                "steps": step,
                "history": history
            })

    return jsonify({
        "status": "max_steps_reached",
        "start_capital": start_capital,
        "final_capital": capital,
        "steps": max_steps,
        "history": history
    })


@app.route("/simulate")
def simulate():
    simulations = 10_000
    start_capital = 100
    target = 1_000_000
    max_steps = 20

    # JSON が大きくなりすぎないよう、返す成功ルートは最大100件にする
    successful_routes_limit = 100

    goal_reached = 0
    total_steps = 0
    total_max_capital = 0

    # 商品別統計
    item_stats = {
        item["name"]: {
            "attempts": 0,
            "successes": 0,
            "failures": 0
        }
        for item in MARKET
    }

    # ステップ別失敗数
    failure_step_stats = {
        str(step): 0
        for step in range(1, max_steps + 1)
    }

    # 資本帯別の生存状況
    capital_band_stats = {
        band: {
            "entries": 0,
            "successful_trades": 0,
            "failed_trades": 0
        }
        for band in CAPITAL_BANDS.values()
    }

    successful_routes = []

    for _ in range(simulations):
        capital = start_capital
        max_capital = capital
        steps = 0
        route = []

        for step in range(1, max_steps + 1):
            item = find_item(capital)

            if item is None:
                break

            steps += 1
            item_name = item["name"]
            capital_band = CAPITAL_BANDS[item["price"]]

            # 商品別統計
            item_stats[item_name]["attempts"] += 1

            # 資本帯別統計
            capital_band_stats[capital_band]["entries"] += 1

            # 到達ルートに今回の商品を記録
            route.append(item_name)

            success = random.random() < item["success_rate"]

            if success:
                item_stats[item_name]["successes"] += 1
                capital_band_stats[capital_band]["successful_trades"] += 1

                capital = item["next_value"]
                max_capital = max(max_capital, capital)

                if capital >= target:
                    goal_reached += 1

                    if len(successful_routes) < successful_routes_limit:
                        successful_routes.append(route)

                    break

            else:
                item_stats[item_name]["failures"] += 1
                capital_band_stats[capital_band]["failed_trades"] += 1
                failure_step_stats[str(step)] += 1

                capital = 0
                break

        total_steps += steps
        total_max_capital += max_capital

    # 商品別の実測成功率
    for stats in item_stats.values():
        attempts = stats["attempts"]
        stats["success_rate_percent"] = round(
            stats["successes"] / attempts * 100, 2
        ) if attempts else 0

    # 資本帯ごとの生存率（その資本帯での交換成功率）
    for stats in capital_band_stats.values():
        entries = stats["entries"]
        stats["survival_rate_percent"] = round(
            stats["successful_trades"] / entries * 100, 2
        ) if entries else 0

    return jsonify({
        "simulations": simulations,
        "start_capital": start_capital,
        "target": target,
        "goal_reached": goal_reached,
        "goal_rate_percent": round(goal_reached / simulations * 100, 2),
        "average_steps": round(total_steps / simulations, 2),
        "average_max_capital": round(total_max_capital / simulations, 2),

        "item_stats": item_stats,
        "failure_step_stats": failure_step_stats,
        "capital_band_stats": capital_band_stats,

        "successful_routes_count": goal_reached,
        "successful_routes_returned": len(successful_routes),
        "successful_routes": successful_routes
    })


if __name__ == "__main__":
    app.run(debug=True)
