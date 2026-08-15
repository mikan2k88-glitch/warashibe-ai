# Warashibe AI v0.7
# 分岐ルート対応の仮想市場エンジン

MARKET = [
    {"price": 100, "name": "わら", "success_rate": 0.80, "next_value": 150},
    {"price": 100, "name": "古い切手", "success_rate": 0.50, "next_value": 300},

    {"price": 150, "name": "小物", "success_rate": 0.75, "next_value": 300},
    {"price": 150, "name": "雑貨セット", "success_rate": 0.55, "next_value": 600},

    {"price": 300, "name": "古本セット", "success_rate": 0.70, "next_value": 600},
    {"price": 300, "name": "限定古書", "success_rate": 0.45, "next_value": 1200},

    {"price": 600, "name": "中古CDセット", "success_rate": 0.65, "next_value": 1200},
    {"price": 600, "name": "アンティーク小物", "success_rate": 0.40, "next_value": 3000},

    {"price": 1200, "name": "中古ゲーム", "success_rate": 0.60, "next_value": 3000},
    {"price": 1200, "name": "コレクターソフト", "success_rate": 0.35, "next_value": 10000},

    {"price": 3000, "name": "電子機器", "success_rate": 0.55, "next_value": 10000},
    {"price": 3000, "name": "工具セット", "success_rate": 0.40, "next_value": 30000},

    {"price": 10000, "name": "ブランド小物", "success_rate": 0.50, "next_value": 30000},
    {"price": 10000, "name": "中古カメラ", "success_rate": 0.35, "next_value": 100000},

    {"price": 30000, "name": "高級中古品", "success_rate": 0.45, "next_value": 100000},
    {"price": 30000, "name": "ヴィンテージ時計", "success_rate": 0.30, "next_value": 300000},

    {"price": 100000, "name": "高額商品", "success_rate": 0.40, "next_value": 300000},
    {"price": 100000, "name": "限定家電", "success_rate": 0.25, "next_value": 1000000},

    {"price": 300000, "name": "希少商品", "success_rate": 0.35, "next_value": 1000000},
]


def find_items(capital):
    """現在の資本で選べる商品をすべて返す"""
    return [item for item in MARKET if item["price"] == capital]
