import hashlib

from dropship.ebay_account_deletion import (
    acknowledge_deletion_notification,
    build_challenge_response,
)


def test_ebay_deletion_challenge_hash_order():
    result = build_challenge_response(
        "abc123",
        verification_token="A" * 32,
        endpoint="https://example.test/ebay/delete",
    )
    expected = hashlib.sha256(
        ("abc123" + ("A" * 32) + "https://example.test/ebay/delete").encode("utf-8")
    ).hexdigest()
    assert result == {"challengeResponse": expected}


def test_ebay_deletion_post_ack_does_not_persist_payload():
    result = acknowledge_deletion_notification({
        "metadata": {"topic": "MARKETPLACE_ACCOUNT_DELETION"},
        "notification": {
            "notificationId": "n1",
            "data": {
                "username": "seller",
                "userId": "u1",
                "eiasToken": "token",
            },
        },
    })
    assert result["status"] == "acknowledged"
    assert result["payload_persisted"] is False
    assert result["user_data_persisted_by_current_pipeline"] is False
    assert result["live_execution_allowed"] is False


def test_flask_ebay_deletion_endpoint_get_and_post(monkeypatch):
    monkeypatch.setenv(
        "EBAY_MARKETPLACE_DELETION_VERIFICATION_TOKEN",
        "B" * 32,
    )
    monkeypatch.setenv(
        "EBAY_MARKETPLACE_DELETION_ENDPOINT",
        "https://warashibe-ai.onrender.com/dropship/ebay/marketplace-account-deletion",
    )

    from app import app

    client = app.test_client()

    challenge = client.get(
        "/dropship/ebay/marketplace-account-deletion?challenge_code=test-code"
    )
    assert challenge.status_code == 200
    assert challenge.is_json is True
    body = challenge.get_json()
    assert len(body["challengeResponse"]) == 64

    notification = client.post(
        "/dropship/ebay/marketplace-account-deletion",
        json={
            "metadata": {"topic": "MARKETPLACE_ACCOUNT_DELETION"},
            "notification": {
                "notificationId": "n1",
                "data": {"userId": "u1"},
            },
        },
    )
    assert notification.status_code == 204
    assert notification.data == b""
