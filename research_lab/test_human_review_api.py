"""PG-016 Human Review API/UI contract tests."""

from datetime import datetime, timezone

from flask import Flask

from research_lab.human_review_api import create_human_review_blueprint


class RecordRepository:
    def __init__(self, record):
        self.record = record

    def get(self, record_key):
        return self.record if record_key == self.record["record_key"] else None

    def latest_for_identity(self, identity_key):
        return self.record if identity_key == self.record["identity_key"] else None


class ReviewRepository:
    def __init__(self):
        self.rows = {}

    def get_by_record_key(self, record_key):
        return self.rows.get(record_key)

    def append(self, decision):
        key = decision["record_key"]
        if key in self.rows:
            raise ValueError("record already reviewed")
        self.rows[key] = dict(decision)
        return dict(decision)


def _record():
    return {
        "version": "0.1",
        "record_key": "pg016-record-001",
        "identity_key": "gtin:4901234567894:JPY",
        "comparison": {
            "status": "comparison_ready",
            "same_identity": True,
            "identity_type": "gtin",
            "identity_value": "4901234567894",
            "currency": "JPY",
            "lowest_asking_price_jpy": 2800,
            "lowest_asking_source": "rakuten_product",
            "highest_asking_price_jpy": 3000,
            "price_spread_jpy": 200,
            "commerce_authorized": False,
        },
        "proposal": {
            "status": "proposal_ready",
            "proposal_type": "review_candidate",
            "candidate_name": "PG-016 Compact Camera",
            "candidate_source": "rakuten_product",
            "candidate_purchase_price_jpy": 2800,
            "reference_price_spread_jpy": 200,
            "physical_fit": "preferred",
            "human_review_required": True,
            "commerce_authorized": False,
            "external_action_authorized": False,
            "purchase_authorized": False,
            "payment_authorized": False,
            "sale_authorized": False,
        },
        "observed_at": "2026-10-02T13:30:00+00:00",
        "captured_at": "2026-10-02T13:31:00+00:00",
        "commerce_authorized": False,
        "external_action_authorized": False,
    }


def main():
    record_repo = RecordRepository(_record())
    review_repo = ReviewRepository()
    fixed_now = lambda: datetime(2026, 10, 2, 13, 45, tzinfo=timezone.utc)

    app = Flask(__name__)
    app.register_blueprint(create_human_review_blueprint(
        record_repository=record_repo,
        review_repository=review_repo,
        review_code_provider=lambda: "8888",
        now_provider=fixed_now,
    ))
    client = app.test_client()

    page = client.get("/review")
    assert page.status_code == 200
    assert b"Human Review" in page.data
    assert b"approve" in page.data
    assert b"reject" in page.data

    unauthorized = client.post("/api/review/latest", json={
        "identity_key": "gtin:4901234567894:JPY",
        "review_code": "wrong",
    })
    assert unauthorized.status_code == 403

    latest = client.post("/api/review/latest", json={
        "identity_key": "gtin:4901234567894:JPY",
        "review_code": "8888",
    })
    assert latest.status_code == 200
    latest_body = latest.get_json()
    assert latest_body["status"] == "review_ready"
    assert latest_body["record"]["record_key"] == "pg016-record-001"
    assert latest_body["commerce_authorized"] is False

    approve = client.post("/api/review/decision", json={
        "record_key": "pg016-record-001",
        "decision": "approve",
        "reason": "reviewed",
        "review_code": "8888",
    })
    assert approve.status_code == 200
    approve_body = approve.get_json()
    assert approve_body["status"] == "review_recorded"
    assert approve_body["decision"]["decision"] == "approve"
    assert approve_body["decision"]["commerce_authorized"] is False
    assert approve_body["execution_triggered"] is False

    duplicate = client.post("/api/review/decision", json={
        "record_key": "pg016-record-001",
        "decision": "reject",
        "reason": "second review",
        "review_code": "8888",
    })
    assert duplicate.status_code == 409

    stale_app = Flask("stale")
    stale_app.register_blueprint(create_human_review_blueprint(
        record_repository=RecordRepository(_record()),
        review_repository=ReviewRepository(),
        review_code_provider=lambda: "8888",
        now_provider=lambda: datetime(2026, 10, 2, 15, 0, tzinfo=timezone.utc),
    ))
    stale_client = stale_app.test_client()
    stale = stale_client.post("/api/review/latest", json={
        "identity_key": "gtin:4901234567894:JPY",
        "review_code": "8888",
    })
    assert stale.status_code == 409
    assert stale.get_json()["reason"] == "record_not_fresh"

    print("PG-016 human review API tests passed")


if __name__ == "__main__":
    main()
