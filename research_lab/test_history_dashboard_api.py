"""PG-019 review/price/history dashboard contract tests."""

from flask import Flask

from research_lab.history_dashboard_api import create_history_dashboard_blueprint


class Repo:
    def __init__(self, rows):
        self.rows = rows

    def history_for_identity(self, identity_key, limit=20):
        return [dict(row) for row in self.rows if row.get("identity_key") == identity_key][:limit]

    def list_for_identity(self, identity_key, limit=20):
        return [dict(row) for row in self.rows if row.get("identity_key") == identity_key][:limit]


def main():
    identity = "gtin:4901234567894:JPY"
    records = Repo([{
        "record_key":"r1","identity_key":identity,
        "comparison":{"lowest_asking_price_jpy":2800,"highest_asking_price_jpy":3200},
        "proposal":{"status":"proposal_ready"},
        "observed_at":"2026-10-02T15:00:00+00:00","captured_at":"2026-10-02T15:01:00+00:00",
    }])
    reviews = Repo([{
        "record_key":"r1","identity_key":identity,"decision":"approve",
        "reviewer_id":"human","reason":"ok","reviewed_at":"2026-10-02T15:02:00+00:00",
    }])
    plans = Repo([{
        "plan_key":"p1","source_record_key":"r1","identity_key":identity,
        "review_decision":"approve","plan":{"execution_mode":"dry_run","commerce_authorized":False},
        "generated_at":"2026-10-02T15:03:00+00:00",
    }])
    economics = Repo([{
        "assessment_key":"e1","plan_key":"p1","identity_key":identity,
        "economics":{"status":"economics_ready","expected_net_profit_jpy":520,
                     "break_even_price_jpy":4399,"stop_loss_price_jpy":3820,
                     "profit_gate":{"economically_viable":True},
                     "commerce_authorized":False},
        "evaluated_at":"2026-10-02T15:04:00+00:00",
    }])

    app = Flask(__name__)
    app.register_blueprint(create_history_dashboard_blueprint(
        record_repository=records,
        review_repository=reviews,
        plan_repository=plans,
        economics_repository=economics,
        review_code_provider=lambda:"8888",
    ))
    client = app.test_client()

    page = client.get("/history")
    assert page.status_code == 200
    assert b"History Dashboard" in page.data

    forbidden = client.post("/api/history", json={"identity_key":identity,"review_code":"wrong"})
    assert forbidden.status_code == 403

    response = client.post("/api/history", json={"identity_key":identity,"review_code":"8888"})
    assert response.status_code == 200
    body=response.get_json()
    assert body["status"]=="history_ready"
    assert body["identity_key"]==identity
    assert len(body["records"])==1
    assert len(body["reviews"])==1
    assert len(body["plans"])==1
    assert len(body["economic_assessments"])==1
    assert body["latest_snapshot"]["lowest_asking_price_jpy"]==2800
    assert body["latest_snapshot"]["review_decision"]=="approve"
    assert body["latest_snapshot"]["expected_net_profit_jpy"]==520
    assert body["commerce_authorized"] is False
    assert body["external_action_authorized"] is False

    print("PG-019 history dashboard tests passed")


if __name__=="__main__":
    main()
