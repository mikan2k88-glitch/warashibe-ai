from flask import Flask, jsonify

from market_engine import choose_random_item, execute_trade

app = Flask(__name__)


@app.route("/")
def home():
    return "Warashibe AI v0.2"


@app.route("/start")
def start():

    capital = 100

    # 現在の資本で商品を選ぶ
    item = choose_random_item(capital)

    if item is None:
        return jsonify({
            "success": False,
            "capital": capital,
            "message": "購入可能な商品がありません"
        })

    # 取引を実行
    result = execute_trade(item)

    return jsonify({
        "selected": item["name"],
        "purchase_price": item["price"],
        "success": result["success"],
        "capital": result["capital"]
    })


if __name__ == "__main__":
    app.run(debug=True)
