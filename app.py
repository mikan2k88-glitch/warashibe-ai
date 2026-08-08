from flask import Flask, jsonify
import random

from market_engine import find_item

app = Flask(__name__)


@app.route("/")
def home():
    return "Warashibe AI v0.3"


@app.route("/journey")
def journey():

    capital = 100
    start_capital = capital

    history = []

    max_steps = 20
    target = 1_000_000

    for step in range(1, max_steps + 1):

        # 現在の資本に対応する商品を探す
        item = find_item(capital)

        if item is None:
            return jsonify({
                "status": "stopped",
                "message": "現在の資本に対応する商品がありません",
                "capital": capital,
                "history": history
            })

        # 取引成功判定
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

            # 目標達成
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


if __name__ == "__main__":
    app.run(debug=True)
