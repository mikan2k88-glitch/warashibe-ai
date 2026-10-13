from unittest.mock import patch

from app import app
from dropship.ebay_user_oauth_v68 import oauth_config


def test_no_credentials_blocks_start(monkeypatch):
    for key in ("EBAY_CLIENT_ID", "EBAY_CLIENT_SECRET", "EBAY_OAUTH_RUNAME", "FLASK_SECRET_KEY"):
        monkeypatch.delenv(key, raising=False)
    with app.test_client() as client:
        response = client.get("/dropship/ebay/oauth/start")
        assert response.status_code == 503
        assert response.json["live_execution_allowed"] is False


def test_invalid_state_blocks_without_network(monkeypatch):
    app.secret_key = "test-only-secret"
    with patch("dropship.ebay_user_oauth_v68.requests.post") as post:
        with app.test_client() as client:
            response = client.get("/dropship/ebay/oauth/callback?code=example&state=wrong")
            assert response.status_code == 400
            assert response.json["reason"] == "invalid_oauth_state"
        post.assert_not_called()


def test_successful_start_is_readonly(monkeypatch):
    for key, value in (
        ("EBAY_CLIENT_ID", "test-client"),
        ("EBAY_CLIENT_SECRET", "test-secret"),
        ("EBAY_OAUTH_RUNAME", "test-runame"),
        ("FLASK_SECRET_KEY", "test-secret"),
    ):
        monkeypatch.setenv(key, value)
    app.secret_key = "test-secret"
    with app.test_client() as client:
        response = client.get("/dropship/ebay/oauth/start")
        assert response.status_code == 302
        assert "sell.account.readonly" in response.location
        assert "response_type=code" in response.location
        assert "test-secret" not in response.location
        assert "no-store" in response.headers["Cache-Control"]


def test_callback_one_shot_evidence(monkeypatch):
    for key, value in (
        ("EBAY_CLIENT_ID", "test-client"),
        ("EBAY_CLIENT_SECRET", "test-secret"),
        ("EBAY_OAUTH_RUNAME", "test-runame"),
        ("FLASK_SECRET_KEY", "test-secret"),
    ):
        monkeypatch.setenv(key, value)
    app.secret_key = "test-secret"

    class Response:
        def raise_for_status(self):
            pass
        def json(self):
            return {"access_token": "sensitive-token"}

    with patch("dropship.ebay_user_oauth_v68.requests.post", return_value=Response()) as post:
        with patch("dropship.ebay_user_oauth_v68.EbayAccountPolicyProvider") as policy:
            policy.return_value.fetch_return_policy_evidence.return_value = {
                "status": "known", "return_terms": {"status": "confirmed"}
            }
            with app.test_client() as client:
                with client.session_transaction() as session:
                    session["ebay_oauth_state"] = "expected"
                response = client.get("/dropship/ebay/oauth/callback?state=expected&code=fake-code")
                assert response.status_code == 200
                assert response.json["live_execution_allowed"] is False
                assert response.json["token_persisted"] is False
                assert "sensitive-token" not in response.get_data(as_text=True)
                replay = client.get("/dropship/ebay/oauth/callback?state=expected&code=fake-code")
                assert replay.status_code == 400
            post.assert_called_once()
