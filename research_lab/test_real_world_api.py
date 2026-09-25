"""Tests for the Warashibe AI real-world API bridge."""

from flask import Flask

from real_world_api import real_world_bp


def _app():
    app = Flask(__name__)
    app.register_blueprint(real_world_bp)
    return app


def _candidate(name, purchase, sale, fees, shipping, days, liquidation):
    return {
        "name": name,
        "item_id": name,
        "provider": "fixture_market",
        "purchase_price_jpy": purchase,
        "estimated_sale_price_jpy": sale,
        "estimated_fees_jpy": fees,
        "estimated_shipping_jpy": shipping,
        "estimated_days_to_sell": days,
        "liquidation_value_jpy": liquidation,
        "market_depth": 0.8,
        "automation_ease": 0.8,
        "confidence": 0.9,
    }


def run_tests():
    app = _app()
    client = app.test_client()

    status = client.get("/real-world/status")
    assert status.status_code == 200
    body = status.get_json()
    assert body["mode"] == "real_world"
    assert body["external_action_authorized"] is False

    invalid = client.post("/real-world/evaluate", json=["bad"])
    assert invalid.status_code == 400

    strong = _candidate("fast-safe", 2600, 4300, 200, 200, 5, 2400)
    single = client.post("/real-world/evaluate", json=strong)
    assert single.status_code == 200
    single_body = single.get_json()
    assert single_body["status"] == "ready_for_human_gate"
    assert single_body["execution_authorized"] is False

    risky = _candidate("risky", 2600, 3900, 300, 300, 25, 1500)
    ranked = client.post("/real-world/evaluate", json={"candidates": [risky, strong]})
    assert ranked.status_code == 200
    ranked_body = ranked.get_json()
    assert ranked_body["candidate"]["name"] == "fast-safe"
    assert ranked_body["commerce_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("real-world API tests passed")
