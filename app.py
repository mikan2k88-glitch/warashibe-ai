from flask import Flask, jsonify
import random

app = Flask(__name__)

# 仮想市場
MARKET = [
    {"name": "わら", "price": 100, "success_rate": 0.8, "next_value": 150},
    {"name": "石", "price": 100, "success_rate": 0.5, "next_value": 300},
    {"name": "古本", "price": 100, "success_rate": 0.3, "next_value": 600},
]

@app.route("/")
def home():
    return "Warashibe AI v0.1"

@app.route("/start")
def start():

    capital = 100

    # 今買える商品
    candidates = [item for item in MARKET if item["price"] <= capital]

    # とりあえずランダムに選ぶ
    item = random.choice(candidates)

    # 売れるかどうか
    success = random.random() < item["success_rate"]

    if success:
        capital = item["next_value"]

    else:
        capital = 0

    return jsonify({
        "selected": item["name"],
        "success": success,
        "capital": capital
    })


if __name__ == "__main__":
    app.run(debug=True)
