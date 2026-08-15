from flask import Flask, jsonify
import random

from market_engine import find_item

app = Flask(__name__)


@app.route("/")
def home():
    return "Warashibe AI v0.5"


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

    simulations = 10000
    start_capital = 100
    target = 1_000_000
    max_steps = 20

    goal_reached = 0
    total_steps = 0
    total_max_capital = 0

    # 商品ごとの統計
    item_stats = {}

    for _ in range(simulations):

        capital = start_capital
        max_capital = capital
        steps = 0

        for _ in range(max_steps):

            item = find_item(capital)

            if item is None:
                break

            steps += 1

            item_name = item["name"]

            # 初めて登場した商品なら統計を作成
            if item_name not in item_stats:
                item_stats[item_name] = {
                    "attempts": 0,
                    "successes": 0,
                    "failures": 0
                }

            # 挑戦回数
            item_stats[item_name]["attempts"] += 1

            success = random.random() < item["success_rate"]

            if success:

                # 成功回数
                item_stats[item_name]["successes"] += 1

                capital = item["next_value"]

                if capital > max_capital:
                    max_capital = capital

                if capital >= target:
                    goal_reached += 1
                    break

            else:

                # 失敗回数
                item_stats[item_name]["failures"] += 1

                capital = 0
                break

        total_steps += steps
        total_max_capital += max_capital

    # 商品ごとの成功率を計算
    for item_name, stats in item_stats.items():

        attempts = stats["attempts"]

        if attempts > 0:
            stats["success_rate_percent"] = round(
                stats["successes"] / attempts * 100,
                2
            )
        else:
            stats["success_rate_percent"] = 0

    goal_rate = goal_reached / simulations * 100
    average_steps = total_steps / simulations
    average_max_capital = total_max_capital / simulations

    return jsonify({
        "simulations": simulations,
        "start_capital": start_capital,
        "target": target,
        "goal_reached": goal_reached,
        "goal_rate_percent": round(goal_rate, 2),
        "average_steps": round(average_steps, 2),
        "average_max_capital": round(average_max_capital, 2),
        "item_stats": item_stats
    })


if __name__ == "__main__":
    app.run(debug=True)
