import random

# 仮想市場の商品データ
MARKET = [
    {
        "name": "わら",
        "price": 100,
        "success_rate": 0.80,
        "next_value": 150
    },
    {
        "name": "石",
        "price": 100,
        "success_rate": 0.50,
        "next_value": 300
    },
    {
        "name": "古本",
        "price": 100,
        "success_rate": 0.30,
        "next_value": 600
    },
]


def get_available_items(capital):
    """現在の資本で購入可能な商品を返す"""
    return [
        item for item in MARKET
        if item["price"] <= capital
    ]


def choose_random_item(capital):
    """現在の資本で購入可能な商品からランダムに選ぶ"""
    candidates = get_available_items(capital)

    if not candidates:
        return None

    return random.choice(candidates)


def execute_trade(item):
    """商品の取引結果をシミュレーションする"""

    success = random.random() < item["success_rate"]

    if success:
        return {
            "success": True,
            "capital": item["next_value"]
        }

    return {
        "success": False,
        "capital": 0
    }
