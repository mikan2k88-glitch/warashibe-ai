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
    assert payload["ceo_attention"]["level"] == "watching"
    assert payload["system_status"]["hq_runner"] == "connected"
    assert payload["system_status"]["commerce_execution"] == "locked_by_human_gate"
    assert payload["strategy_learning"]["status"] == "active"
    assert payload["strategy_learning"]["minimum_distinct_sources"] == 2
    assert payload["strategy_learning"]["production_rule_auto_change"] is False

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
    assert "CEO Attention" in html
    assert "P2 実商品候補" in html
    assert "仕入候補を見る" in html
    assert "売却実績を見る" in html
    assert "P1–P7 開発完了 7/7" in html
    assert "システム状態" in html
    assert "Strategy Learning Loop" in html
    assert "P2シャドー検証" in html
    assert "本番ルールは自動変更しません" in html

    print("CEO Dashboard contract tests passed")


if __name__ == "__main__":
    main()
