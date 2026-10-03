"""CEO Dashboard contract tests."""

from app import app
from research_lab.hq_dashboard import build_hq_dashboard_payload


def main():
    payload = build_hq_dashboard_payload()
    assert payload["status"] == "hq_dashboard_ready"
    assert payload["current_phase"] == "P2"
    assert payload["development_endpoint"] == "P7"
    assert payload["current_bottleneck"] == "real_external_single_item_pilot_not_verified"
    assert payload["candidate"]["state"] == "live_screened_hold"
    assert payload["candidate"]["item_name"] == "ウルトラ怪獣モンスターファーム"
    assert payload["candidate"]["go_to_p3"] is False
    assert payload["candidate"]["economics"]["remote_purchase_profit_jpy"] < 0
    assert payload["candidate"]["economics"]["local_pickup_profit_jpy"] > 0
    assert len(payload["development_summary"]) == 7
    assert payload["human_gate"]["required_for_real_commerce"] is True

    client = app.test_client()

    api = client.get("/hq/api")
    assert api.status_code == 200
    api_payload = api.get_json()
    assert api_payload["current_phase"] == "P2"
    assert api_payload["candidate"]["state"] == "live_screened_hold"

    page = client.get("/hq")
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    assert "Warashibe CEO Dashboard" in html
    assert "現在フェーズ" in html
    assert "P2" in html
    assert "開発サマリー" in html
    assert "ウルトラ怪獣モンスターファーム" in html
    assert "P3へ上げない" in html
    assert "Human Gate" in html

    print("CEO Dashboard contract tests passed")


if __name__ == "__main__":
    main()
